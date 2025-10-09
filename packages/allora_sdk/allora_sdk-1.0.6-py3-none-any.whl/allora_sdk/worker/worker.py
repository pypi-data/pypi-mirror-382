"""
Allora Worker

This module provides an easy-to-use interface for ML developers to submit predictions to the
Allora network. It handles WebSocket subscriptions, signal handling, and resource cleanup
across different execution environments (shell, Jupyter, CoLab).
"""

import asyncio
from dataclasses import dataclass
from getpass import getpass
import os
import signal
import sys
import requests
import logging
import time
from typing import Callable, Optional, AsyncIterator, Tuple, Type, Union, Awaitable, cast
import dill

from cosmpy.aerial.client import TxResponse
from cosmpy.aerial.wallet import LocalWallet, PrivateKey
from cosmpy.mnemonic import generate_mnemonic
from allora_sdk.protos.cosmos.bank.v1beta1 import QueryBalanceRequest
import async_timeout

from allora_sdk.protos.emissions.v3 import ReputerValueBundle, ValueBundle
from allora_sdk.rpc_client.client import AlloraRPCClient
from allora_sdk.rpc_client.client_websocket_events import EventAttributeCondition
from allora_sdk.rpc_client.config import AlloraNetworkConfig, AlloraWalletConfig
from allora_sdk.rpc_client.tx_manager import FeeTier, TxError
from allora_sdk.protos.emissions.v9 import (
    EventReputerSubmissionWindowClosed,
    EventReputerSubmissionWindowOpened,
    EventWorkerSubmissionWindowOpened,
    EventWorkerSubmissionWindowClosed,
    CanSubmitWorkerPayloadRequest,
    GetUnfulfilledWorkerNoncesRequest,
    IsWorkerRegisteredInTopicIdRequest,
)
from allora_sdk.utils import Context, TimestampOrderedSet, format_allo_from_uallo
from allora_sdk.logging_config import setup_sdk_logging

logger = logging.getLogger("allora_sdk")


@dataclass
class PredictionResult:
    prediction: float
    tx_result: TxResponse

class WorkerNotWhitelistedError(Exception):
    pass

@dataclass
class _StopQueue:
    pass

PredictionItem = Union[PredictionResult, Exception, _StopQueue]
PredictFnResultType = str | float
PredictFnSync = Callable[[int], PredictFnResultType]
PredictFnAsync = Callable[[int], Awaitable[PredictFnResultType]]
PredictFn = Union[PredictFnSync, PredictFnAsync]

SubmissionWindowOpenedEvent = Union[EventWorkerSubmissionWindowOpened, EventReputerSubmissionWindowOpened]

class AlloraWorker:
    """
    ML-friendly Allora network worker with async generator interface.
    
    Provides automatic WebSocket subscription management, environment-aware signal handling,
    and graceful resource cleanup for submitting predictions to Allora network topics.
    """

    @classmethod
    def inferer(
        cls,
        run: PredictFn | Tuple[str, str],
        wallet: Optional[AlloraWalletConfig] = None,
        network: Optional[AlloraNetworkConfig] = AlloraNetworkConfig.testnet(),
        api_key: Optional[str] = None,
        topic_id: int = 69,
        fee_tier: FeeTier = FeeTier.STANDARD,
        polling_interval: int = 120,
        debug: bool = False,
    ):
        """
        Create an AlloraWorker configured as an inferer.

        Args:
            run: Function that returns prediction values (str or float)
            run_pkl: Path to pickle file containing a 'run' function
            wallet: Wallet configuration (private key, mnemonic, or file)
            network: Allora network configuration (testnet/mainnet/custom)
            api_key: API key for testnet faucet (if needed)
            topic_id: The Allora network topic ID to submit predictions to
            fee_tier: Transaction fee tier (ECO/STANDARD/PRIORITY)
            polling_interval: Interval in seconds to poll for new submission windows
            debug: Enable debug logging

        Returns:
            An instance of AlloraWorker configured as an inferer
        """
        return cls(
            run=run,
            wallet=wallet,
            network=network,
            api_key=api_key,
            topic_id=topic_id,
            fee_tier=fee_tier,
            polling_interval=polling_interval,
            submission_window_event_type=EventWorkerSubmissionWindowOpened,
            debug=debug,
        )

    # @classmethod
    # def reputer(
    #     cls,
    #     run: Optional[PredictFn] = None,
    #     run_pkl: Optional[str] = None,
    #     wallet: Optional[AlloraWalletConfig] = None,
    #     network: Optional[AlloraNetworkConfig] = AlloraNetworkConfig.testnet(),
    #     api_key: Optional[str] = None,
    #     topic_id: int = 69,
    #     fee_tier: FeeTier = FeeTier.STANDARD,
    #     polling_interval: int = 120,
    #     debug: bool = False,
    # ):
    #     """
    #     Create an AlloraWorker configured as a reputer.

    #     Args:
    #         run: Function that returns prediction values (str or float)
    #         run_pkl: Path to pickle file containing a 'run' function
    #         wallet: Wallet configuration (private key, mnemonic, or file)
    #         network: Allora network configuration (testnet/mainnet/custom)
    #         api_key: API key for testnet faucet (if needed)
    #         topic_id: The Allora network topic ID to submit predictions to
    #         fee_tier: Transaction fee tier (ECO/STANDARD/PRIORITY)
    #         polling_interval: Interval in seconds to poll for new submission windows
    #         debug: Enable debug logging

    #     Returns:
    #         An instance of AlloraWorker configured as a reputer
    #     """
    #     return cls(
    #         run=run,
    #         run_pkl=run_pkl,
    #         wallet=wallet,
    #         network=network,
    #         api_key=api_key,
    #         topic_id=topic_id,
    #         fee_tier=fee_tier,
    #         polling_interval=polling_interval,
    #         submission_window_event_type=EventReputerSubmissionWindowOpened,
    #         debug=debug,
    #     )


    def __init__(
        self,
        run: PredictFn | Tuple[str, str],
        wallet: Optional[AlloraWalletConfig] = None,
        network: Optional[AlloraNetworkConfig] = AlloraNetworkConfig.testnet(),
        api_key: Optional[str] = None,
        topic_id: int = 69,
        fee_tier: FeeTier = FeeTier.STANDARD,
        polling_interval: int = 120,
        submission_window_event_type: Type[SubmissionWindowOpenedEvent] = EventWorkerSubmissionWindowOpened,
        debug: bool = False,
    ) -> None:
        """
        Initialize the Allora worker.
        
        Args:
            topic_id: The Allora network topic ID to submit predictions to
            _user_callback: Function that returns prediction values (str or float)
            wallet: Wallet configuration (private key, mnemonic, or file)
            api_key: API key for testnet faucet (if needed)
            fee_tier: Transaction fee tier (ECO/STANDARD/PRIORITY)
            log_level: `logging` package levels
            submission_window_event_type: Event type to listen for submission windows (worker, reputer, forecaster)
            debug: Enable debug logging
        """
        if isinstance(run, tuple):
            pkl_file, fn_name = run
            mod = dill.load_module_asdict(pkl_file)
            if mod is None:
                raise ValueError("Could not load the pickle file")

            fn = mod.get(fn_name)
            if fn is None:
                raise ValueError("Pickle file must contain a 'run' function")
            run = cast(PredictFn, fn)

        if not run:
            raise ValueError("'run' parameter must be provided")
        if not callable(run):
            raise ValueError("The 'run' function must be callable")
        self._user_callback = run


        self.topic_id = topic_id
        self._user_callback = run
        self.fee_tier = fee_tier
        self.polling_interval = polling_interval
        self.api_key = api_key
        self.submission_window_event_type = submission_window_event_type
        self.submitted_nonces = TimestampOrderedSet()

        setup_sdk_logging(debug=debug)

        self.wallet = self._init_wallet(wallet)
        if not self.wallet:
            raise Exception('no wallet')

        self.client = AlloraRPCClient(
            wallet=AlloraWalletConfig(wallet=self.wallet),
            network=network,
            debug=debug,
        )
        self._ctx: Optional[Context] = None
        self._prediction_queue: Optional[asyncio.Queue[PredictionItem]] = None
        self._subscription_id: Optional[str] = None


        if self.api_key:
            self._maybe_faucet_request()


    def _init_wallet(self, wallet: AlloraWalletConfig | None):
        if wallet:
            if wallet.private_key:
                return LocalWallet(PrivateKey(bytes.fromhex(wallet.private_key)))
            if wallet.mnemonic:
                return LocalWallet.from_mnemonic(wallet.mnemonic, "allo")

        if wallet:
            mnemonic_file = wallet.mnemonic_file or ".allora_key"
        else:
            mnemonic_file = ".allora_key"

        if os.path.exists(mnemonic_file):
            with open(mnemonic_file, "r") as f:
                mnemonic = f.read().strip()
                return LocalWallet.from_mnemonic(mnemonic, "allo")
        else:
            print("Enter your Allora wallet mnemonic or press <ENTER> to have one generated for you.")
            mnemonic = getpass("Mnemonic: ").strip()
            if not mnemonic or  mnemonic == "":
                mnemonic = generate_mnemonic()

            with open(mnemonic_file, "w") as f:
                f.write(mnemonic)
            print(f"Mnemonic saved to {mnemonic_file}")
            return LocalWallet.from_mnemonic(mnemonic, "allo")

    def _maybe_faucet_request(self):
        MIN_ALLO = 100000000

        resp = self.client.bank.balance(QueryBalanceRequest(address=str(self.wallet.address()), denom="uallo"))
        if resp.balance is None:
            logger.error(f"Could not check balance for {str(self.wallet.address())}")
            return
        balance = int(resp.balance.amount)
        balance_formatted = format_allo_from_uallo(balance)
        logger.info(f"Worker wallet {str(self.wallet.address())} balance: {balance_formatted}")
        if self.client.network.chain_id != "allora-testnet-1":
            return
        if not self.client.network.faucet_url:
            return
        if balance >= MIN_ALLO:
            return
        logger.info(f"    Requesting ALLO from testnet faucet...")

        while True:
            try:
                faucet_resp = requests.post(self.client.network.faucet_url + "/api/request", data={
                    "chain": "allora-testnet-1",
                    "address": str(self.wallet.address()),
                }, headers={
                    "x-api-key": self.api_key,
                })
                faucet_resp.raise_for_status()
                logger.info(f"    Request sent...")

                while True:
                    time.sleep(5)
                    resp = self.client.bank.balance(QueryBalanceRequest(address=str(self.wallet.address()), denom="uallo"))
                    if resp.balance is None:
                        logger.error(f"    Could not check balance for {str(self.wallet.address())}")
                        continue
                    balance = int(resp.balance.amount)
                    balance_formatted = format_allo_from_uallo(balance)
                    logger.info(f"    Balance: {balance_formatted}")
                    if balance >= MIN_ALLO:
                        return
            except requests.HTTPError as err:
                if err.response.status_code == 429:
                    logger.error(f"    Too many faucet requests. Try sending ALLO to your worker's wallet manually from another wallet, or visit https://faucet.testnet.allora.network")
                    self.stop()
                    sys.exit(-1)
                logger.error(f"    Error requesting funds from wallet: {err}")
            except Exception as err:
                logger.error(f"    Error requesting funds from wallet: {err}")

            time.sleep(15)

        
    def _detect_environment(self) -> str:
        if "ipykernel" in sys.modules:
            return "jupyter"
        elif "google.colab" in sys.modules:
            return "colab"
        else:
            return "shell"
            
    def _setup_signal_handlers(self, ctx: Context):
        env = self._detect_environment()
        
        if env == "shell":
            # Track if we've already received a SIGINT
            sigint_received = False
            
            def signal_handler(signum, frame):
                nonlocal sigint_received
                
                if signum == signal.SIGINT:
                    if not sigint_received:
                        # First Ctrl-C: graceful shutdown
                        logger.info("Received SIGINT, initiating graceful shutdown (Ctrl-C again to force exit)")
                        sigint_received = True
                        ctx.cancel()
                    else:
                        # Second Ctrl-C: force exit
                        logger.warning("Force exiting due to repeated SIGINT")
                        import sys
                        sys.exit(1)
                else:
                    # SIGTERM: always graceful
                    logger.info(f"Received signal {signum}, initiating graceful shutdown")
                    ctx.cancel()
                
            for sig in (signal.SIGINT, signal.SIGTERM):
                signal.signal(sig, signal_handler)

        elif env in ("jupyter", "colab"):
            logger.debug(f"Running in {env} environment, using manual stop mechanisms")

    async def run(self, timeout: Optional[float] = None) -> AsyncIterator[PredictionResult |  Exception]:
        """
        Run the worker and yield predictions as they"re submitted.
        
        This is the main entry point for inference providers. It returns an async
        generator that yields prediction submission results as they happen.
        
        Args:
            timeout: Optional timeout for the entire run (useful in notebooks)
            
        Yields:
            str: Prediction submission results with transaction links
            
        Example:
            >>> worker = AlloraWorker(topic_id=13, _user_callback=my_model.predict)
            >>> async for result in worker.run():
            ...     print(f"Submitted: {result}")
        """
        if self._ctx and not self._ctx.is_cancelled():
            raise RuntimeError("Worker is already running")
            
        ctx = Context()
        self._ctx = ctx
        self._prediction_queue = asyncio.Queue()
        
        self._setup_signal_handlers(ctx)
        
        logger.debug(f"Starting Allora worker for topic {self.topic_id}")
        
        try:
            resp = self.client.emissions.query.is_worker_registered_in_topic_id(
                IsWorkerRegisteredInTopicIdRequest(
                    topic_id=self.topic_id,
                    address=str(self.wallet.address()),
                ),
            )
            if not resp.is_registered:
                logger.debug(f"Registering worker {str(self.wallet.address())} for topic {self.topic_id}")
                resp = await self.client.emissions.tx.register(
                    topic_id=self.topic_id,
                    owner_addr=str(self.wallet.address()),
                    sender_addr=str(self.wallet.address()),
                    is_reputer=False,
                    fee_tier=FeeTier.PRIORITY,
                )

            if timeout:
                try:
                    async with async_timeout.timeout(timeout):
                        async for prediction in self._run_with_context(ctx):
                            yield prediction
                except asyncio.TimeoutError:
                    logger.debug(f"Worker stopped after {timeout}s timeout")
            else:
                async for prediction in self._run_with_context(ctx):
                    yield prediction
                    
        except (asyncio.CancelledError, KeyboardInterrupt):
            logger.debug("Worker stopped by cancellation")
            ctx.cancel()
        finally:
            await self._cleanup(ctx)

    async def _run_with_context(self, ctx: Context) -> AsyncIterator[PredictionResult |  Exception]:
        polling = asyncio.create_task(self._polling_worker(ctx))
        ctx.add_cleanup_task(polling)

        await self._subscribe_websocket_events()

        cleanup_task = asyncio.create_task(self._monitor_cancellation(ctx))
        ctx.add_cleanup_task(cleanup_task)
        
        try:
            while not ctx.is_cancelled():
                if self._prediction_queue is None:
                    break
                try:
                    # use short timeout to allow cancellation checks
                    result = await asyncio.wait_for(self._prediction_queue.get(), timeout=1.0)
                    if isinstance(result, _StopQueue):  # Sentinel value for shutdown
                        break
                    yield result
                except asyncio.TimeoutError:
                    continue  # check cancellation and try again
                    
        except asyncio.CancelledError:
            # propagate ctx cancellation
            raise
            
    async def _monitor_cancellation(self, ctx: Context):
        await ctx.wait_for_cancellation()
        if self._prediction_queue is not None:
            try:
                self._prediction_queue.put_nowait(_StopQueue())
            except asyncio.QueueFull:
                pass

    async def _polling_worker(self, ctx: Context):
        logger.info(f"🔄 Starting polling worker for topic {self.topic_id}")
        
        while not ctx.is_cancelled():
            logger.info(f"🔄 Polling worker checking topic {self.topic_id}")
            try:
                await self._maybe_submit(ctx)
            except asyncio.CancelledError:
                self.stop()
                break
            except asyncio.TimeoutError:
                pass
            except WorkerNotWhitelistedError:
                logger.error(f"The wallet {str(self.wallet.address())} is not whitelisted on topic {self.topic_id}.  Contact the topic creator.")
                self.stop()
                break
            except Exception as e:
                logger.error(f"Error in polling worker: {e}")
                pass

            await asyncio.sleep(self.polling_interval)
        
        logger.debug(f"🔄 Polling worker stopped for topic {self.topic_id}")
    

    async def _subscribe_websocket_events(self):
        self._subscription_id = await self.client.events.subscribe_new_block_events_typed(
            self.submission_window_event_type,
            [ EventAttributeCondition("topic_id", "=", f'"{str(self.topic_id)}"') ],
            self._handle_submission_window_opened,
        )
        await self.client.events.subscribe_new_block_events_typed(
            EventWorkerSubmissionWindowClosed,
            [ EventAttributeCondition("topic_id", "=", f'"{str(self.topic_id)}"') ],
            lambda evt, height: logger.info(f"✨ Worker submission window closed (topic {evt.topic_id}, nonce {evt.nonce_block_height}, height {height})"),
        )
        await self.client.events.subscribe_new_block_events_typed(
            EventReputerSubmissionWindowOpened,
            [ EventAttributeCondition("topic_id", "=", f'"{str(self.topic_id)}"') ],
            lambda evt, height: logger.info(f"🚀 Reputer submission window opened (topic {evt.topic_id}, nonce {evt.nonce_block_height}, height {height})"),
        )
        await self.client.events.subscribe_new_block_events_typed(
            EventReputerSubmissionWindowClosed,
            [ EventAttributeCondition("topic_id", "=", f'"{str(self.topic_id)}"') ],
            lambda evt, height: logger.info(f"✨ Reputer submission window closed (topic {evt.topic_id}, nonce {evt.nonce_block_height}, height {height})"),
        )


    async def _handle_submission_window_opened(self, event: SubmissionWindowOpenedEvent, height: int):
        ctx = self._ctx
        if ctx is None or ctx.is_cancelled():
            return

        logger.info(f"🚀 Worker submission window opened (topic {self.topic_id}, nonce {event.nonce_block_height}, height {height})")
        
        try:
            await self._maybe_submit(ctx, event.nonce_block_height)
        except Exception as e:
            logger.error(f"Error handling event: {e}")


    async def _maybe_submit(self, ctx: Context, nonce: Optional[int] = None):
        if ctx.is_cancelled():
            return

        can_submit_resp = self.client.emissions.query.can_submit_worker_payload(
            CanSubmitWorkerPayloadRequest(
                address=str(self.wallet.address()),
                topic_id=self.topic_id,
            )
        )
        if not can_submit_resp.can_submit_worker_payload:
            logger.error(f"The wallet {str(self.wallet.address())} is not whitelisted on topic {self.topic_id}.  Contact the topic creator.")
            self.stop()
            return

        resp = self.client.emissions.query.get_unfulfilled_worker_nonces(
            GetUnfulfilledWorkerNoncesRequest(topic_id=self.topic_id)
        )
        nonces     = { x.block_height for x in resp.nonces.nonces } if resp.nonces is not None else set()
        new_nonces = { n for n in nonces if n not in self.submitted_nonces }

        if nonce is not None:
            new_nonces.add(nonce)

        logger.info(f"Checking topic {self.topic_id}: {len(nonces)} unfulfilled nonces {nonces}, our unfulfilled nonces {new_nonces if len(new_nonces) > 0 else '{}'}")

        for nonce in new_nonces:
            if not self._ctx or self._ctx.is_cancelled():
                break

            logger.info(f"👉 Found new nonce {nonce} for topic {self.topic_id}, submitting...")

            try:
                result = await self._submit(nonce)
                if isinstance(result, TxError):
                    if result.code == 78 or result.code == 75: # already submitted
                        self.submitted_nonces.add(nonce)
                        logger.info(f"⚠️ Already submitted for this epoch: topic_id={self.topic_id} nonce={nonce}")
                    elif "inference already submitted" in result.message: # this is a different "already submitted" from allora-chain that has no error code, awesome
                        self.submitted_nonces.add(nonce)
                        logger.info(f"⚠️ Already submitted for this epoch: topic_id={self.topic_id} nonce={nonce}")
                    elif result.code != 0:
                        logger.error(f"❌ Error submitting for this epoch: topic_id={self.topic_id} nonce={nonce} {str(result)}")
                        self.submitted_nonces.add(nonce)

                elif isinstance(result, Exception):
                    logger.error(f"❌ Unknown error submitting for nonce {nonce}: {str(result)} {type(result)}")
                    self.submitted_nonces.add(nonce)

                elif result:
                    logger.info(f"✅ Successfully submitted: topic={self.topic_id} nonce={nonce}")
                    logger.info(f"    - Transaction hash: {result.tx_result.txhash}")
                    self.submitted_nonces.add(nonce)

                resp = self.client.bank.balance(QueryBalanceRequest(address=str(self.wallet.address()), denom="uallo"))
                if resp.balance is None:
                    logger.error(f"Could not check balance for {str(self.wallet.address())}")
                    continue
                balance = int(resp.balance.amount)
                balance_formatted = format_allo_from_uallo(balance)
                logger.info(f"    - Wallet balance: {balance_formatted}")
                self._maybe_faucet_request()

            except Exception as e:
                logger.error(f"Error submitting for nonce {nonce}: {e}")

            finally:
                # disallow unbounded growth of the nonce tracking set with a reasonable default
                self.submitted_nonces.prune_older_than(2 * 60 * 60)

                # inform whatever is listening about the result
                if (
                    ctx.is_cancelled() == False and
                    self._prediction_queue is not None and
                    result is not None
                ):
                    await self._prediction_queue.put(result)


    async def _submit(self, nonce: int):
        if not self.wallet:
            return Exception('no wallet')

        try:
            if asyncio.iscoroutinefunction(self._user_callback):
                prediction: PredictFnResultType = await self._user_callback(nonce)
            else:
                # Run sync prediction in executor to avoid blocking
                loop = asyncio.get_event_loop()
                prediction: PredictFnResultType = await loop.run_in_executor(None, self._user_callback, nonce)
        except Exception as err:
            logger.debug(f"Prediction function failed: {err}")
            return err

        try:
            resp = await (await self.client.emissions.tx.insert_worker_payload(
                topic_id=self.topic_id,
                inference_value=str(prediction),
                nonce=nonce,
                fee_tier=self.fee_tier
            )).wait()

            if resp.code != 0:
                return TxError(
                    codespace=resp.codespace,
                    code=resp.code,
                    tx_hash=resp.txhash,
                    message=resp.raw_log,
                )

            return PredictionResult(prediction=float(prediction), tx_result=resp)
            
        except Exception as err:
            return err

    async def _cleanup(self, ctx: Context):
        logger.debug("Cleaning up worker resources")
        
        if self._subscription_id:
            try:
                await self.client.events.unsubscribe(self._subscription_id)
                logger.debug("WebSocket subscription cancelled")
            except Exception as e:
                logger.warning(f"Error during unsubscribe: {e}")
            finally:
                self._subscription_id = None
        
        await ctx.cleanup()
        self._prediction_queue = None
        self._ctx = None
        
        logger.debug("Worker cleanup completed")


    def stop(self):
        """Manually stop the worker (useful in notebook environments)."""
        if self._ctx:
            logger.debug("Manually stopping worker")
            self._ctx.cancel()



# class InfererUseCase:
#     def _ensure_registration(self):
#         resp = self.client.emissions.query.is_worker_registered_in_topic_id(
#             IsWorkerRegisteredInTopicIdRequest(
#                 topic_id=self.topic_id,
#                 address=str(self.wallet.address()),
#             ),
#         )
#         if not resp.is_registered:
#             logger.debug(f"Registering worker {str(self.wallet.address())} for topic {self.topic_id}")
#             resp = await self.client.emissions.tx.register(
#                 topic_id=self.topic_id,
#                 owner_addr=str(self.wallet.address()),
#                 sender_addr=str(self.wallet.address()),
#                 is_reputer=False,
#                 fee_tier=FeeTier.PRIORITY,
#             )


