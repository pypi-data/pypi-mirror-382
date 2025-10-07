from .websocket import WSClient, make_client_ssl_context
import copy
import asyncio
import os, sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, "fbs_gen"))

from .subscribe import (
    ClientLedgerMetaSubscription,
    ClientDomainMetaSubscription,
    ClientDomainsSubscription,
    ClientDomainMarketDataSubscription,
    ClientTradeSubscription,
    ClientPositionsSubscription,
    ClientFillsSubscription,
    ClientOpenOrdersSubscription,
    ClientLeaderboardSubscription,
    ClientIssuedOptionsSubscription,
    ClientL2BookSubscription
)

from .request import (
    ClientSetSessionRequest,
    ClientAddOrderRequest,
    ClientCancelOrderRequest,
    ClientDepositRequest,
    ClientWithdrawRequest,
    ClientConversionRequest,
    ClientExerciseOptionRequest,
    ClientIssueOptionRequest
)

from .fbs_gen.gateway.ServerResponse import ServerResponse
from .fbs_gen.gateway.ServerResponseUnion import ServerResponseUnion
from .fbs_gen.gateway.SubscriptionResponse import SubscriptionResponse
from .fbs_gen.gateway.DomainsStream import DomainsStream
from .fbs_gen.gateway.DomainMetaStream import DomainMetaStream
from .fbs_gen.gateway.DomainMarketDataStream import DomainMarketDataStream
from .fbs_gen.gateway.LedgerMetaStream import LedgerMetaStream
from .fbs_gen.gateway.OpenOrdersStream import OpenOrdersStream
from .fbs_gen.gateway.WsOpenOrders import WsOpenOrders
from .fbs_gen.gateway.OpenOrdersSnapshot import OpenOrdersSnapshot
from .fbs_gen.gateway.OrderDeltasData import OrderDeltasData
from .fbs_gen.gateway.FillsStream import FillsStream
from .fbs_gen.gateway.PositionsStream import PositionsStream
from .fbs_gen.gateway.PositionsSnapshot import PositionsSnapshot
from .fbs_gen.gateway.PositionDeltasData import PositionDeltasData
from .fbs_gen.gateway.WsPositions import WsPositions
from .fbs_gen.gateway.L2BookStream import L2BookStream
from .fbs_gen.gateway.IssuedOptionsStream import IssuedOptionsStream
from .fbs_gen.gateway.WsIssuedOptions import WsIssuedOptions
from .fbs_gen.gateway.TradesStream import TradesStream
from .fbs_gen.gateway.AddOrderResponse import AddOrderResponse
from .fbs_gen.gateway.ErrorMessage import ErrorMessage
from .fbs_gen.gateway.SimpleSuccessResponse import SimpleSuccessResponse
from .fbs_gen.gateway.AuctionMetaUnion import AuctionMetaUnion
from .fbs_gen.gateway.TwoSidedMeta import TwoSidedMeta
from .fbs_gen.gateway.SecondPriceMeta import SecondPriceMeta
from .fbs_gen.gateway.IssuedOptionsSnapshot import IssuedOptionsSnapshot
from .fbs_gen.gateway.IssuedOptionsDeltaData import IssuedOptionsDeltaData

from .fbs_gen.client.Tif import Tif
from .fbs_gen.client.OrderType import OrderType
from .fbs_gen.gateway.Side import Side

def b2s(b):
    return b.decode("utf-8") if b is not None else None

def require_account_and_domain(func):
    def wrapper(self, *args, **kwargs):
        assert self.domain_metadata['Domain'], "No domain set"
        assert self.account, "No account set"
        return func(self, *args, **kwargs)
    return wrapper

class OracleClient:
    def __init__(self):
        print(f"\033[1;32mWelcome to HUQT OracleClient!\033[0m")
        self.listen_task: asyncio.Task | None = None
        self.account = None

        self.subscriptions: dict[int, list] = {}
        self.subscription_tasks: dict[str, tuple[int, str]] = {}
        self.pending_orders: dict[str, tuple[int, dict]] = {}
        self.pending_requests: dict[str, tuple[int, str, dict]] = {}

        self.oracle_metadata = {
            'Available Domains': [],
            'Ledger Metadata': [],
        }

        self.domain_metadata = {
            'Domain': None,
            'Available Markets': {},
            'Markets Metadata': [],
            'Conversion Markets Metadata': [],
            'Options Markets Metadata': [],
            'Auctions Markets Metadata': [],
            'Markets state': []
        }

        self.open_orders: dict[str, list] = {}
        self.open_auction_orders: dict[str, list] = {}
        self.positions: dict[str, int] = {}
        self.recent_fills: list[dict] = []
        self.book: dict[str, dict[str, int]] = {}
        self.recent_trades: dict[str, list] = {}
        self.self_issued_options_quantity: dict[str, int] = {}
        self.global_issued_options_quantity: dict[str, int] = {}
    
    #############################################################################################
    """Query the states of the object"""
    def get_self_open_orders(self) -> dict[str, list]:
        return copy.deepcopy(self.open_orders)
    
    def get_self_open_auction_orders(self) -> dict[str, list]:
        return copy.deepcopy(self.open_auction_orders)
    
    def get_self_positions(self) -> dict[str, int]:
        return copy.deepcopy(self.positions)
    
    def get_self_recent_fills(self) -> list[dict]:
        return copy.deepcopy(self.recent_fills)

    def get_book(self) -> dict[str, dict[str, int]]:
        return copy.deepcopy(self.book)
    
    def get_recent_trades(self) -> dict[str, list]:
        return copy.deepcopy(self.recent_trades)
    
    def get_oracle_metadata(self) -> dict[str, list]:
        return copy.deepcopy(self.oracle_metadata)

    def get_domain_metadata(self) -> dict:
        return copy.deepcopy(self.domain_metadata)
    
    def get_self_pending_orders(self) -> dict[str, tuple[int, dict]]:
        return copy.deepcopy(self.pending_orders)
    
    def get_self_pending_requests(self) -> dict[str, tuple[int, str, dict]]:
        return copy.deepcopy(self.pending_requests)
    
    def get_issued_options_quantity(self, is_global = False) -> dict[str, int]:
        if is_global:
            return copy.deepcopy(self.global_issued_options_quantity)
        return copy.deepcopy(self.self_issued_options_quantity)
    
    #############################################################################################
    """Handlers for sending messages"""
    async def __ledger_meta_subscription(self, subscribe: bool):
        uuid, raw_msg = ClientLedgerMetaSubscription(subscribe=subscribe).to_bytes()
        self.subscription_tasks[uuid] = (9, "")
        await self.ws_client.send(raw_msg)

    async def __domain_subscription(self, subscribe: bool):
        uuid, raw_msg = ClientDomainsSubscription(subscribe=subscribe).to_bytes()
        self.subscription_tasks[uuid] = (7, "")
        await self.ws_client.send(raw_msg)

    async def __domain_meta_subscription(self, subscribe: bool, domain: str):
        uuid, raw_msg = ClientDomainMetaSubscription(subscribe=subscribe, domain=domain).to_bytes()
        self.subscription_tasks[uuid] = (6, domain)
        await self.ws_client.send(raw_msg)
    
    async def __domain_market_subscription(self, subscribe: bool, domain: str):
        uuid, raw_msg = ClientDomainMarketDataSubscription(subscribe=subscribe, domain=domain).to_bytes()
        self.subscription_tasks[uuid] = (8, domain)
        await self.ws_client.send(raw_msg)
    
    async def __open_orders_subscription(self, subscribe: bool, domain: str, account: str):
        uuid, raw_msg = ClientOpenOrdersSubscription(subscribe=subscribe, domain=domain, account=account).to_bytes()
        self.subscription_tasks[uuid] = (3, domain)
        await self.ws_client.send(raw_msg)
    
    async def __positions_subscription(self, subscribe: bool, domain: str, account: str):
        uuid, raw_msg = ClientPositionsSubscription(subscribe=subscribe, domain=domain, account=account).to_bytes()
        self.subscription_tasks[uuid] = (4, domain)
        await self.ws_client.send(raw_msg)
    
    async def __fills_subscription(self, subscribe: bool, domain: str, account: str):
        uuid, raw_msg = ClientFillsSubscription(subscribe=subscribe, domain=domain, account=account).to_bytes()
        self.subscription_tasks[uuid] = (2, domain)
        await self.ws_client.send(raw_msg)

    ## TODO, response doesn't exists yet...
    async def __leaderboard_subscription(self, subscribe: bool, domain: str):
        uuid, raw_msg = ClientLeaderboardSubscription(subscribe=subscribe, domain=domain).to_bytes()
        self.subscription_tasks[uuid] = (5, domain)
        await self.ws_client.send(raw_msg)

    async def __issued_options_subscription(self, subscribe: bool, domain: str, account: str):
        uuid, raw_msg = ClientIssuedOptionsSubscription(subscribe=subscribe, domain=domain, account=account).to_bytes()
        self.subscription_tasks[uuid] = (11, domain)
        await self.ws_client.send(raw_msg)
    
    async def __l2_book_subscription(self, subscribe: bool, domain: str, market: str):
        uuid, raw_msg = ClientL2BookSubscription(subscribe=subscribe, domain=domain, market=market).to_bytes()
        self.subscription_tasks[uuid] = (10, domain)
        await self.ws_client.send(raw_msg)
    
    async def __trade_subscription(self, subscribe: bool, domain: str, market: str):
        uuid, raw_msg = ClientTradeSubscription(subscribe=subscribe, domain=domain, market=market).to_bytes()
        self.subscription_tasks[uuid] = (1, domain + ':' + market)
        await self.ws_client.send(raw_msg)
    
    ## for the user send messages
    async def place_limit_order(self, market: str, side: int, price: int, size: int, tif: int):
        try:
            await self.__place_limit_order(market, side, price, size, tif)
        except Exception as e:
            print(f"Error placing limit order. {e}")
        
    @require_account_and_domain
    async def __place_limit_order(self, market: str, side: int, price: int, size: int, tif: int):
        assert market in self.domain_metadata['Available Markets']['markets'],f"Invalid market: {market}. Available Markets are: {self.domain_metadata['Available Markets']}"
        assert side in [0, 1], f"Invalid side enumerate: {side}"
        assert tif in [0, 1, 2], f"Invalid tif enumerate: {side}"
        assert size > 0, "Size must be positive for orders"
        assert price > 0, "Price must be positive for orders"

        uuid, raw_msg = ClientAddOrderRequest(
            domain = self.domain_metadata['Domain'],
            market = market,
            side = side,
            px = price,
            sz = size,
            collateral = 0,
            order_type = OrderType.Limit,
            tif = tif
        ).to_bytes(self.account)
        self.pending_orders[uuid] = (int(time.time() * 1000), {
            'market': market,
            'order type': 'limit',
            'side': 'buy' if side == Side.Buy else 'sell',
            'price': price,
            'size': size,
        })
        await self.ws_client.send(raw_msg)
    
    async def place_market_order(self, market: str, side: int, collateral: int):
        try:
            await self.__place_market_order(market, side, collateral)
        except Exception as e:
            print(f"Error placing market order. {e}")
    
    @require_account_and_domain
    async def __place_market_order(self, market: str, side: int, collateral: int):
        assert market in self.domain_metadata['Available Markets']['markets'],f"Invalid market: {market}. Available Markets are: {self.domain_metadata['Available Markets']}"
        assert side in [0, 1], f"Invalid side enumerate: {side}"
        assert collateral > 0, "Collateral must be positive for market orders"

        uuid, raw_msg = ClientAddOrderRequest(
            domain = self.domain_metadata['Domain'],
            market = market,
            side = side,
            px = 0,
            sz = 0,
            collateral = collateral,
            order_type = OrderType.Market,
            tif = Tif.Ioc
        ).to_bytes(self.account)
        self.pending_orders[uuid] = (int(time.time() * 1000), {
            'market': market,
            'order type': 'market',
            'side': 'buy' if side == Side.Buy else 'sell',
            'collateral': collateral,
        })
        await self.ws_client.send(raw_msg)

    async def place_auction_order(self, market: str, price: int):
        try:
            await self.__place_auction_order(market, price)
        except Exception as e:
            print(f"Error placing auction order. {e}")
    
    @require_account_and_domain
    async def __place_auction_order(self, market: str, price: int):
        assert market in self.domain_metadata['Available Markets']['auctions'],f"Invalid auction market: {market}. Available Markets are: {self.domain_metadata['Available Markets']}"
        assert price > 0, "Price must be positive for auction orders"

        uuid, raw_msg = ClientAddOrderRequest(
            domain = self.domain_metadata['Domain'],
            market = market,
            side = Side.Buy,
            px = price,
            sz = 1,
            collateral = 0,
            order_type = OrderType.Auction,
            tif = Tif.Alo
        ).to_bytes(self.account)
        self.pending_orders[uuid] = (int(time.time() * 1000), {
            'market': market,
            'order type': 'Auction',
            'side': 'buy',
            'price': price,
        })
        await self.ws_client.send(raw_msg)
    
    async def cancel_order(self, market: str, order_id: int):
        try:
            await self.__cancel_order(market, order_id)
        except Exception as e:
            print(f"Error canceling order. {e}")
    
    @require_account_and_domain
    async def __cancel_order(self, market: str, order_id: int):
        assert market in self.domain_metadata['Available Markets']['markets'], f"Invalid market: {market}. Available Markets are: {self.domain_metadata['Available Markets']}"
        
        uuid, raw_msg = ClientCancelOrderRequest(
            domain = self.domain_metadata['Domain'],
            market = market,
            order_id = order_id
        ).to_bytes(self.account)
        self.pending_requests[uuid] = (int(time.time() * 1000), 'cancel', {
            'market': market,
            'order id': order_id
        })
        await self.ws_client.send(raw_msg)

    async def deposit(self, symbol: str, amount: int):
        try:
            await self.__deposit(symbol, amount)
        except Exception as e:
            print(f"Error depositing: {e}")
    
    @require_account_and_domain
    async def __deposit(self, symbol: str, amount: int):
        assert symbol in [k.split(":")[0] for k in self.positions.keys()], "Invalid symbol"

        uuid, raw_msg = ClientDepositRequest(
            domain=self.domain_metadata['Domain'],
            symbol=symbol,
            amount=amount
        ).to_bytes(self.account)
        self.pending_requests[uuid] = (int(time.time() * 1000), 'deposit', {
            'symbol': symbol,
            'amount': amount
        })
        await self.ws_client.send(raw_msg)
    
    async def withdraw(self, symbol: str, amount: int):
        try:
            await self.__withdraw(symbol, amount)
        except Exception as e:
            print(f"Error withdrawing: {e}")
    
    @require_account_and_domain
    async def __withdraw(self, symbol: str, amount: int):
        assert symbol in [k.split(":")[0] for k in self.positions.keys()], "Invalid symbol"

        uuid, raw_msg = ClientWithdrawRequest(
            domain=self.domain_metadata['Domain'],
            symbol=symbol,
            amount=amount
        ).to_bytes(self.account)
        self.pending_requests[uuid] = (int(time.time() * 1000), 'withdraw', {
            'symbol': symbol,
            'amount': amount
        })
        print(uuid)
        print(self.pending_requests)
        await self.ws_client.send(raw_msg)
    
    async def convert(self, conversion: str, size: int):
        try:
            await self.__convert(conversion, size)
        except Exception as e:
            print(f"Error converting: {e}")
    
    @require_account_and_domain
    async def __convert(self, conversion: str, size: int):
        assert conversion in self.domain_metadata['Available Markets']['conversions'], f"Invalid conversion market: {conversion}. Available conversions markets are: {self.domain_metadata['Available Markets']['conversions']}"

        uuid, raw_msg = ClientConversionRequest(
            domain=self.domain_metadata['Domain'],
            conversion=conversion,
            size=size
        ).to_bytes(self.account)
        self.pending_requests[uuid] = (int(time.time() * 1000), 'convert', {
            'conversion': conversion,
            'size': size
        })
        await self.ws_client.send(raw_msg)
    
    async def issue_option(self, name, size):
        try:
            await self.__issue_options(name, size)
        except Exception as e:
            print(f"Error issuing options: {e}")
    
    @require_account_and_domain
    async def __issue_options(self, name, size):
        assert name in self.domain_metadata['Available Markets']['options'], "Invalid options name"

        uuid, raw_msg = ClientIssueOptionRequest(
            domain=self.domain_metadata['Domain'],
            name=name,
            size=size
        ).to_bytes(self.account)
        self.pending_requests[uuid] = (int(time.time() * 1000), 'issue option', {
            'name': name,
            'size': size
        })
        await self.ws_client.send(raw_msg)
    
    async def exercise_option(self, name, size):
        try:
            await self.__exercise_option(name, size)
        except Exception as e:
            print(f"Error issuing options: {e}")
    
    @require_account_and_domain
    async def __exercise_option(self, name, size):
        assert name in self.domain_metadata['Available Markets']['options'], "Invalid options name"

        uuid, raw_msg = ClientExerciseOptionRequest(
            domain=self.domain_metadata['Domain'],
            name=name,
            size=size
        ).to_bytes(self.account)
        self.pending_requests[uuid] = (int(time.time() * 1000), 'exercise option', {
            'name': name,
            'size': size
        })
        await self.ws_client.send(raw_msg)

    #############################################################################################
    """Handlers for receiving messages"""
    async def message_handler(self, msg: bytes):
        buf = bytearray(msg)
        root = ServerResponse.GetRootAs(buf, 0)
        tbl = root.Response()
    
        match root.ResponseType():
            case ServerResponseUnion.SubscriptionResponse:
                self.__handle_subscription_response(tbl)
            case ServerResponseUnion.LedgerMetaStream:
                self.__handle_ledger_meta_stream(tbl)
            case ServerResponseUnion.DomainsStream:
                self.__handle_domains_stream(tbl)
            case ServerResponseUnion.DomainMetaStream:
                self.__handle_domain_meta_stream(tbl)
            case ServerResponseUnion.DomainMarketDataStream:
                self.__handle_domain_market_data_stream(tbl)
            case ServerResponseUnion.OpenOrdersStream:
                self.__handle_open_orders_stream(tbl)
            case ServerResponseUnion.PositionsStream:
                self.__handle_positions_stream(tbl)
            case ServerResponseUnion.FillsStream:
                self.__handle_fills_stream(tbl)
            case ServerResponseUnion.L2BookStream:
                self.__handle_l2_book_stream(tbl)
            case ServerResponseUnion.IssuedOptionsStream:
                self.__handle_issued_options_stream(tbl)
            case ServerResponseUnion.TradesStream:
                self.__handle_trade_stream(tbl)
            
            case ServerResponseUnion.AddOrderResponse:
                self.__handle_add_order_response(tbl)
            case ServerResponseUnion.ErrorMessage:
                self.__handle_error_message(tbl)
            case ServerResponseUnion.SimpleSuccessResponse:
                self.__handle_simple_success(tbl)
            
            case ServerResponseUnion.LeaderboardStream:
                # TODO not implemented
                pass
            
            case _:
                print(f"Unhandled message type: {root.ResponseType()}")

    def __handle_add_order_response(self, tbl):
        aor = AddOrderResponse()
        aor.Init(tbl.Bytes, tbl.Pos)
        if b2s(aor.Uuid()) in self.pending_orders:
            del self.pending_orders[b2s(aor.Uuid())]
        else:
            print(f"\033[1;33m[Warning]\033[0m received success from uuid: {b2s(aor.Uuid())}", end=" ")
            print("but this order was not placed through the current python client")

    def __handle_error_message(self, tbl):
        em = ErrorMessage()
        em.Init(tbl.Bytes, tbl.Pos)
        if b2s(em.Uuid()) in self.pending_orders:
            print(f"\033[1;33m[Warning]\033[0m order {b2s(em.Uuid())}", end=" ")
            print(f"placed at time {self.pending_orders[b2s(em.Uuid())][0]}", end = " ")
            print(f"with details {self.pending_orders[b2s(em.Uuid())][1]}", end=" ")
            print(f"failed from \'{b2s(em.Message())}\'")
            del self.pending_orders[b2s(em.Uuid())]
        elif b2s(em.Uuid()) in self.pending_requests:
            print(f"\033[1;33m[Warning]\033[0m request {b2s(em.Uuid())}", end=" ")
            print(f"placed at time {self.pending_requests[b2s(em.Uuid())][0]}", end = " ")
            print(f"of type: {self.pending_requests[b2s(em.Uuid())][1]}", end = " ")
            print(f"and details {self.pending_requests[b2s(em.Uuid())][2]}", end=" ")
            print(f"failed from \'{b2s(em.Message())}\'")
            del self.pending_requests[b2s(em.Uuid())]
        else:
            print(f"\033[1;33m[Warning]\033[0m received failure from uuid: {b2s(em.Uuid())}", end=" ")
            print("but this order was not placed through the current python client")
    
    def __handle_simple_success(self, tbl):
        ssr = SimpleSuccessResponse()
        ssr.Init(tbl.Bytes, tbl.Pos)

        if b2s(ssr.Uuid()) in self.subscription_tasks:
            del self.subscription_tasks[b2s(ssr.Uuid())]
        elif b2s(ssr.Uuid()) in self.pending_requests:
            del self.pending_requests[b2s(ssr.Uuid())]
        else:
            print(f"\033[1;33m[Warning]\033[0m received success from uuid: {b2s(ssr.Uuid())}", end=" ")
            print("but this order was not placed through the current python client")
    
    def __handle_subscription_response(self, tbl):
        sub = SubscriptionResponse()
        sub.Init(tbl.Bytes, tbl.Pos)
        uuid = b2s(sub.Uuid())
        task_done = self.subscription_tasks[uuid]
        del self.subscription_tasks[uuid]

        if sub.Subscribe():
            if task_done[0] in self.subscriptions:
                self.subscriptions[task_done[0]].append(task_done[1])
            else:
                self.subscriptions[task_done[0]] = [task_done[1]]
        else:
            self.subscriptions[task_done[0]].remove(task_done[1])
            if self.subscriptions[task_done[0]] == []:
                del self.subscriptions[task_done[0]]
    
    def __handle_ledger_meta_stream(self, tbl):
        lms = LedgerMetaStream()
        lms.Init(tbl.Bytes, tbl.Pos)

        new_ledger_meta = []
        for i in range(lms.SymbolsLength()):
            symbol = lms.Symbols(i)
            new_ledger_meta.append({
                "name": b2s(symbol.Name()),
                "movable": symbol.Movable()
            })
        
        if not self.oracle_metadata['Ledger Metadata']:
            self.oracle_metadata['Ledger Metadata'] = new_ledger_meta
        elif self.oracle_metadata['Ledger Metadata'] == new_ledger_meta:
            pass
        else:
            self.oracle_metadata['Ledger Metadata'] = new_ledger_meta
            print("\033[1;31m[WARNING]\033[0m Ledger metadata changed during runtime!")
    
    def __handle_domains_stream(self, tbl):
        ds = DomainsStream()
        ds.Init(tbl.Bytes, tbl.Pos)
        if not self.oracle_metadata['Available Domains']:
            self.oracle_metadata['Available Domains'] = [b2s(ds.Domains(i)) for i in range(ds.DomainsLength())]
            print("Available domains:", self.oracle_metadata['Available Domains'])
        elif self.oracle_metadata['Available Domains'] == [b2s(ds.Domains(i)) for i in range(ds.DomainsLength())]:
            pass
        else:
            self.oracle_metadata['Available Domains'] = [b2s(ds.Domains(i)) for i in range(ds.DomainsLength())]
            print("\033[1;31m[WARNING]\033[0m Domanins changed during runtime!")
            print("Available domains:", self.oracle_metadata['Available Domains'])
    
    def __handle_domain_meta_stream(self, tbl):
        dms = DomainMetaStream()
        dms.Init(tbl.Bytes, tbl.Pos)

        auctions_name = []
        for i in range(dms.AuctionsLength()):
            am = dms.Auctions(i)
            u = am.Meta()
            match am.MetaType():
                case AuctionMetaUnion.TwoSidedMeta:
                    tsm = TwoSidedMeta()
                    tsm.Init(u.Bytes, u.Pos)
                    auctions_name.append(b2s(tsm.Name()))
                case AuctionMetaUnion.SecondPriceMeta:
                    spm = SecondPriceMeta()
                    spm.Init(u.Bytes, u.Pos)
                    auctions_name.append(b2s(spm.Name()))
        
        market_names = {
            "conversions": [b2s(dms.Conversions(i).Name()) for i in range(dms.ConversionsLength())],
            "markets": [b2s(dms.Markets(i).Name()) for i in range(dms.MarketsLength())],
            "options": [b2s(dms.Options(i).Name()) for i in range(dms.OptionsLength())],
            "auctions": auctions_name,
        }

        if not self.domain_metadata['Available Markets']:
            self.domain_metadata['Available Markets'] = market_names
            print("Available markets:", self.domain_metadata['Available Markets'])
            self.__construct_market_meta(dms)
        elif self.domain_metadata['Available Markets'] == market_names:
            pass
        else:
            self.domain_metadata['Available Markets'] = market_names
            print("\033[1;31m[WARNING]\033[0m Markets changed during runtime!")
            print("Available markets:", self.domain_metadata['Available Markets'])
            self.__construct_market_meta(dms)

    def __construct_market_meta(self, dms: DomainMetaStream):
        self.domain_metadata['Markets Metadata'] = []
        self.domain_metadata['Conversion Markets Metadata'] = []
        self.domain_metadata['Options Markets Metadata'] = []
        self.domain_metadata['Auctions Markets Metadata'] = []

        for i in range(dms.ConversionsLength()):
            conv = dms.Conversions(i)
            self.domain_metadata['Conversion Markets Metadata'].append({
                "name": b2s(conv.Name()),
                "from": [(b2s(conv.From(j).Symbol()), conv.From(j).Amount()) for j in range(conv.FromLength())],
                "to": [(b2s(conv.To(j).Symbol()), conv.To(j).Amount()) for j in range(conv.ToLength())],
            })
        
        for i in range(dms.MarketsLength()):
            mkt = dms.Markets(i)
            self.domain_metadata['Markets Metadata'].append({
                "name": b2s(mkt.Name()),
                "base": b2s(mkt.Base()),
                "quote": b2s(mkt.Quote()),
                "flat_fee": mkt.FlatFee(),
                "taker_fee": mkt.TakerFee(),
                "maker_fee": mkt.MakerFee(),
                "fee_denom": mkt.FeeDenom()
            })
        
        for i in range(dms.OptionsLength()):
            opt = dms.Options(i)
            self.domain_metadata['Options Markets Metadata'].append({
                "name": b2s(opt.Name()),
                "from": [(b2s(opt.From(j).Symbol()), opt.From(j).Amount()) for j in range(opt.FromLength())],
                "to": [(b2s(opt.To(j).Symbol()), opt.To(j).Amount()) for j in range(opt.ToLength())],
                "flat_fee": [(b2s(opt.FlatFee(j).Symbol()), opt.FlatFee(j).Amount()) for j in range(opt.FlatFeeLength())],
                "option": b2s(opt.Option())
            })
        
        for i in range(dms.AuctionsLength()):
            am = dms.Auctions(i)
            u = am.Meta()
            match am.MetaType():
                case AuctionMetaUnion.TwoSidedMeta:
                    tsm = TwoSidedMeta()
                    tsm.Init(u.Bytes, u.Pos)
                    self.domain_metadata['Auctions Markets Metadata'].append({
                        "name": b2s(tsm.Name()),
                        "type": "two sided",
                        "quote": b2s(tsm.Quote()),
                        "flat fee": tsm.FlatFee(),
                        "base": b2s(tsm.Base())
                    })
                case AuctionMetaUnion.SecondPriceMeta:
                    spm = SecondPriceMeta()
                    spm.Init(u.Bytes, u.Pos)
                    self.domain_metadata['Auctions Markets Metadata'].append({
                        "name": b2s(spm.Name()),
                        "type": "second price",
                        "quote": b2s(spm.Quote()),
                        "flat fee": spm.FlatFee(),
                        "prize": [(b2s(spm.Prize(i).Symbol()), spm.Prize(i).Amount()) for i in range(spm.PrizeLength())]
                    })
            
    def __handle_domain_market_data_stream(self, tbl):
        dmds = DomainMarketDataStream()
        dmds.Init(tbl.Bytes, tbl.Pos)

        self.domain_metadata['Markets state'] = []
        for i in range(dmds.MarketsLength()):
            mkt = dmds.Markets(i)
            self.domain_metadata['Markets state'].append({
                "name": b2s(mkt.Name()),
                "best_bid": mkt.BestBid(),
                "best_offer": mkt.BestOffer(),
                "mark_px": mkt.MarkPx(),
                "vol": mkt.Vol(),
                "ntnl_vol": mkt.NtnlVol()
            })

    def __handle_open_orders_stream(self, tbl):
        oos = OpenOrdersStream()
        oos.Init(tbl.Bytes, tbl.Pos)

        match oos.OrdersType():
            case WsOpenOrders.OpenOrdersSnapshot:
                snapshot = OpenOrdersSnapshot()
                orders = oos.Orders()
                snapshot.Init(orders.Bytes, orders.Pos)

                self.open_orders = {}
                for i in range(snapshot.ClobOrdersLength()):
                    order = snapshot.ClobOrders(i)
                    market = b2s(order.Market())
                    order_json = {
                        "oid": order.Oid(),
                        "price": order.Px(),
                        "size": order.Sz(),
                        "side": order.Side()
                    }
                    if market not in self.open_orders:
                        self.open_orders[market] = [order_json]
                    else:
                        self.open_orders[market].append(order_json)
                    
                self.open_auction_orders = {}
                for i in range(snapshot.AuctionOrdersLength()):
                    order = snapshot.AuctionOrders(i)
                    market = b2s(order.Market())
                    order_json = {
                        "oid": order.Oid(),
                        "price": order.Px(),
                        "size": order.Sz(),
                        "side": order.Side()
                    }
                    if market not in self.open_auction_orders:
                        self.open_auction_orders[market] = [order_json]
                    else:
                        self.open_auction_orders[market].append(order_json)

            case WsOpenOrders.OrderDeltasData:
                deltas = OrderDeltasData()
                orders = oos.Orders()
                deltas.Init(orders.Bytes, orders.Pos)

                for i in range(deltas.ClobDeltasLength()):
                    delta = deltas.ClobDeltas(i)
                    market = b2s(delta.Market())
                    order_json = {
                        "oid": delta.Oid(),
                        "px": delta.Px(),
                        "new_sz": delta.NewSz(),
                        "side": delta.Side()
                    }

                    if delta.IsAdd():
                        market = b2s(delta.Market())
                        if market not in self.open_orders:
                            self.open_orders[market] = [order_json]
                        else:
                            self.open_orders[market].append(order_json)
                    if delta.IsRemove():
                        for i, order in enumerate(self.open_orders[market]):
                            if order['oid'] == delta.Oid():
                                del self.open_orders[market][i]
                                break
                    if not delta.IsAdd() and not delta.IsRemove():
                        for order in self.open_orders[market]:
                            if order['oid'] == delta.Oid():
                                order['size'] = delta.NewSz()
                                break
                
                for i in range(deltas.AuctionDeltasLength()):
                    delta = deltas.AuctionDeltas(i)
                    market = b2s(delta.Market())
                    order_json = {
                        "oid": delta.Oid(),
                        "px": delta.Px(),
                        "new_sz": delta.NewSz(),
                        "side": delta.Side()
                    }

                    if delta.IsAdd():
                        market = b2s(delta.Market())
                        if market not in self.open_auction_orders:
                            self.open_auction_orders[market] = [order_json]
                        else:
                            self.open_auction_orders[market].append(order_json)
                    if delta.IsRemove():
                        for i, order in enumerate(self.open_auction_orders[market]):
                            if order['oid'] == delta.Oid():
                                del self.open_auction_orders[market][i]
                                break
                    if not delta.IsAdd() and not delta.IsRemove():
                        for order in self.open_auction_orders[market]:
                            if order['oid'] == delta.Oid():
                                order['size'] = delta.NewSz()
                                break
            case _:
                print("Unknown open orders type")
            
    def __handle_positions_stream(self, tbl):
        ps = PositionsStream()
        ps.Init(tbl.Bytes, tbl.Pos)

        match ps.PositionsType():
            case WsPositions.PositionsSnapshot:
                snapshot = PositionsSnapshot()
                positions = ps.Positions()
                snapshot.Init(positions.Bytes, positions.Pos)

                self.positions = {}
                for i in range(snapshot.PositionsLength()):
                    position = snapshot.Positions(i)
                    name = b2s(position.Symbol()) + ':' + ('main' if position.AccountType() == 0 else 'collateral')
                    self.positions[name] = position.Position()
                print("Current Account Positions:", self.positions)
            case WsPositions.PositionDeltasData:
                deltas = PositionDeltasData()
                positions = ps.Positions()
                deltas.Init(positions.Bytes, positions.Pos)

                if deltas.DeltasLength() > 0:
                    for i in range(deltas.DeltasLength()):
                        delta = deltas.Deltas(i)
                        name = b2s(delta.Symbol()) + ':' + ('main' if delta.AccountType() == 0 else 'collateral')
                        if name not in self.positions:
                            self.positions[name] = 0
                        self.positions[name] += delta.Delta()
            case _:
                print("Unknown positions type")

    def __handle_fills_stream(self, tbl):
        fs = FillsStream()
        fs.Init(tbl.Bytes, tbl.Pos)

        if fs.IsSnapshot():
            self.recent_fills = []
        for i in range(fs.FillsLength()):
            fill = fs.Fills(i)
            self.recent_fills.append({
                "market": b2s(fill.Market()),
                "oid": fill.Oid(),
                "price": fill.Px(),
                "size": fill.Sz(),
                "side": fill.Side(),
                "is_taker": fill.IsTaker(),
                "time": fill.Time(),
            })
        
        if len(self.recent_fills) > 20:
            l = len(self.recent_fills)
            self.recent_fills = self.recent_fills[l-20:]
    
    def __handle_issued_options_stream(self, tbl):
        ios = IssuedOptionsStream()
        ios.Init(tbl.Bytes, tbl.Pos)
        match ios.IssuancesType():
            case WsIssuedOptions.IssuedOptionsSnapshot:
                snapshot = IssuedOptionsSnapshot()
                iss = ios.Issuances()
                snapshot.Init(iss.Bytes, iss.Pos)

                for i in range(snapshot.IssuancesLength()):
                    order = snapshot.Issuances(i)
                    self.self_issued_options_quantity[b2s(order.Name())] = order.Position()
                
                for i in range(snapshot.GlobalIssuancesLength()):
                    order = snapshot.GlobalIssuances(i)
                    self.global_issued_options_quantity[b2s(order.Name())] = order.Position()

            case WsIssuedOptions.IssuedOptionsDeltaData:
                deltas = IssuedOptionsDeltaData()
                iss = ios.Issuances()
                deltas.Init(iss.Bytes, iss.Pos)

                for i in range(deltas.DeltasLength()):
                    delta = deltas.Deltas(i)
                    self.self_issued_options_quantity[b2s(delta.Name())] += delta.Delta()

                for i in range(deltas.DeltasLength()):
                    delta = deltas.GlobalDeltas(i)
                    self.global_issued_options_quantity[b2s(delta.Name())] += delta.Delta()

            case _:
                print("Unknown issued options type")
    
    def __handle_l2_book_stream(self, tbl):
        lbs = L2BookStream()
        lbs.Init(tbl.Bytes, tbl.Pos)
        market = b2s(lbs.Market())
        self.book[market] = {}
        self.book[market]['bids'] = [{'price': lbs.Bids(i).Px(), 'size': lbs.Bids(i).Sz()}  for i in range(lbs.BidsLength())]
        self.book[market]['asks'] = [{'price': lbs.Asks(i).Px(), 'size': lbs.Asks(i).Sz()}  for i in range(lbs.AsksLength())]
    
    def __handle_trade_stream(self, tbl):
        ts = TradesStream()
        ts.Init(tbl.Bytes, tbl.Pos)
        market = b2s(ts.Market())
        if ts.IsSnapshot():
            self.recent_trades[market] = []

        for i in range(ts.TradesLength()):
            trade = ts.Trades(i)
            self.recent_trades[market].append({
                'price': trade.Px(),
                'size': trade.Sz(),
                'taker side': trade.TakerSide(),
                'time': trade.Time()
            })
        
        if len(self.recent_trades[market]) > 20:
            l = len(self.recent_trades[market])
            self.recent_trades[market] = self.recent_trades[market][l-20:]

    #############################################################################################
    """Handlers for starting and stopping the client"""
    async def start_client(self,
                           account: str,
                           api_key: str,
                           domain: str,
                           print_oracle_metadata: bool = False,
                           print_domain_metadata: bool = False
                           ):
        ctx = make_client_ssl_context()
        print("created ctx: ", ctx)
        self.ws_client = WSClient("wss://api.oracle.huqt.xyz/ws", api_key, ctx)
        await self.ws_client.connect()
        self.listen_task = asyncio.create_task(
            self.ws_client.listen(self.message_handler)
        )
        print("WebSocket client started, listening for messages...")

        await self.__domain_subscription(subscribe=True)
        await self.__ledger_meta_subscription(subscribe=True)

        counter = 0
        while self.subscription_tasks:
            await asyncio.sleep(0.01)
            counter += 1
            assert counter < 300, "Oracle is unavailable, timed out after 3 seconds."
        
        if print_oracle_metadata:
            print("Oracle Metadata:", self.oracle_metadata)
        await self.__set_account_and_domain(account, domain, print_domain_metadata)

    async def __set_session(self):
        uuid, raw_msg = ClientSetSessionRequest(
            domain = self.domain_metadata['Domain'],
        ).to_bytes(self.account)
        self.subscription_tasks[uuid] = (10, "set session")
        await self.ws_client.send(raw_msg)

    async def __set_account_and_domain(self, account: str, domain: str, print_metadata: bool):
        assert not self.account, "Account already set"
        assert not self.domain_metadata['Domain'], "Domain already set"        
        assert domain in self.oracle_metadata['Available Domains'], f"Invalid domain: {domain}. Available Domains are: {self.oracle_metadata['Available Domains']}"
        self.account = account
        self.domain_metadata['Domain'] = domain
        
        await self.__set_session()

        counter = 0
        while self.subscription_tasks:
            await asyncio.sleep(0.01)
            counter += 1
            assert counter < 300, f"Failed to receive a validation from server."

        await self.__domain_meta_subscription(subscribe=True, domain=self.domain_metadata['Domain'])
        await self.__domain_market_subscription(subscribe=True, domain=self.domain_metadata['Domain'])
        await self.__open_orders_subscription(subscribe=True, domain=self.domain_metadata['Domain'], account=self.account)
        await self.__positions_subscription(subscribe=True, domain=self.domain_metadata['Domain'], account=self.account)
        await self.__fills_subscription(subscribe=True, domain=self.domain_metadata['Domain'], account=self.account)
        await self.__issued_options_subscription(subscribe=True, domain=self.domain_metadata['Domain'], account = self.account)
        # await self.__leaderboard_subscription(subscribe=True, domain=self.domain_metadata['Domain']) # does not work TODO

        counter = 0
        while self.subscription_tasks:
            await asyncio.sleep(0.01)
            counter += 1
            assert counter < 300, f"Failed to Subscribe to the {self.domain_metadata['Domain']} domain. Timed out after 3 seconds"

        print("\033[1;32mOracleClient started successfully!\033[0m")
        # print(f"\033[1;32mSelected {domain} domain successfully!\033[0m")
        if print_metadata:
            print(f"Domain Metadata: {self.domain_metadata}")
    
    @require_account_and_domain
    async def subscribe_market(self, market: str):
        counter = 0
        while not self.domain_metadata['Available Markets']:
            await asyncio.sleep(0.01)
            counter += 1
            assert counter < 300, "No domains available, timed out after 3 seconds"

        assert market in self.domain_metadata['Available Markets']['markets'], f"Invalid market: {market}. Available Markets are: {self.domain_metadata['Available Markets']['markets']}"
        # self.markets.append(market)

        await self.__l2_book_subscription(subscribe=True, domain=self.domain_metadata['Domain'], market=market)
        await self.__trade_subscription(subscribe=True, domain=self.domain_metadata['Domain'], market=market)

        counter = 0
        while self.subscription_tasks:
            await asyncio.sleep(0.01)
            counter += 1
            assert counter < 300, f"Failed to Subscribe to the {market} domain. Timed out after 3 seconds"

        print(f"Subscribed to the {market} market successfully!")
    
    async def stop_client(self):
        if self.listen_task and not self.listen_task.done():
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass