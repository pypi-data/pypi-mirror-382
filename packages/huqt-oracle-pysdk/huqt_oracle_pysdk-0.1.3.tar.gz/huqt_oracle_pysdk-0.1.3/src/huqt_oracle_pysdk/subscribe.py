import uuid
import flatbuffers

from .fbs_gen.client.ClientRequestUnion import ClientRequestUnion
from .fbs_gen.client import (
    ClientRequest,
    SubscriptionRequest,
)

from .fbs_gen.gateway.Subscription import Subscription
from .fbs_gen.gateway import (
    TradeSubscription,
    FillsSubscription,
    OpenOrdersSubscription,
    PositionsSubscription,
    L2BookSubscription,
    DomainMetaSubscription,
    DomainsSubscription,
    DomainMarketDataSubscription,
    LedgerMetaSubscription,
    LeaderboardSubscription,
    IssuedOptionsSubscription,
)


class ClientLedgerMetaSubscription():
    def __init__(self, subscribe: bool):
        self.subscribe = subscribe

    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        LedgerMetaSubscription.LedgerMetaSubscriptionStart(builder)
        ledger_meta_subscription = LedgerMetaSubscription.LedgerMetaSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, ledger_meta_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.LedgerMetaSubscription)
        ledger_meta_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, ledger_meta_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)

        builder.Finish(request)
        return u, bytes(builder.Output())

class ClientDomainMetaSubscription():
    def __init__(self, subscribe: bool, domain: str):
        self.subscribe = subscribe
        self.domain = domain

    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_offset = builder.CreateString(self.domain)

        DomainMetaSubscription.DomainMetaSubscriptionStart(builder)
        DomainMetaSubscription.AddDomain(builder, domain_offset)
        domain_meta_subscription = DomainMetaSubscription.DomainMetaSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, domain_meta_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.DomainMetaSubscription)
        domain_meta_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, domain_meta_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)

        builder.Finish(request)
        return u, bytes(builder.Output())

class ClientDomainsSubscription():
    def __init__(self, subscribe: bool):
        self.subscribe = subscribe

    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        DomainsSubscription.DomainsSubscriptionStart(builder)
        domains_subscription = DomainsSubscription.DomainsSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, domains_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.DomainsSubscription)
        domains_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, domains_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)   

        builder.Finish(request)
        return u, bytes(builder.Output())
    
class ClientDomainMarketDataSubscription():
    def __init__(self, subscribe: bool, domain: str):
        self.subscribe = subscribe
        self.domain = domain

    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_offset = builder.CreateString(self.domain)

        DomainMarketDataSubscription.DomainMarketDataSubscriptionStart(builder)
        DomainMarketDataSubscription.AddDomain(builder, domain_offset)
        domain_market_data_subscription = DomainMarketDataSubscription.DomainMarketDataSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, domain_market_data_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.DomainMarketDataSubscription)
        domain_market_data_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, domain_market_data_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)

        builder.Finish(request)
        return u, bytes(builder.Output())

class ClientFillsSubscription():
    def __init__(self, subscribe: bool, domain: str, account: str):
        self.subscribe = subscribe
        self.domain = domain
        self.account = account
    
    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_offset = builder.CreateString(self.domain)
        account_offset = builder.CreateString(self.account)

        FillsSubscription.FillsSubscriptionStart(builder)
        FillsSubscription.AddDomain(builder, domain_offset)
        FillsSubscription.AddAccount(builder, account_offset)
        fills_subscription = FillsSubscription.FillsSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, fills_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.FillsSubscription)
        fills_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, fills_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)

        builder.Finish(request)
        return u, bytes(builder.Output())

class ClientOpenOrdersSubscription():
    def __init__(self, subscribe: bool, domain: str, account: str):
        self.subscribe = subscribe
        self.domain = domain
        self.account = account

    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_offset = builder.CreateString(self.domain)
        account_offset = builder.CreateString(self.account)

        OpenOrdersSubscription.OpenOrdersSubscriptionStart(builder)
        OpenOrdersSubscription.AddDomain(builder, domain_offset)
        OpenOrdersSubscription.AddAccount(builder, account_offset)
        open_orders_subscription = OpenOrdersSubscription.OpenOrdersSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, open_orders_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.OpenOrdersSubscription)
        open_orders_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, open_orders_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)

        builder.Finish(request)
        return u, bytes(builder.Output())

class ClientPositionsSubscription():
    def __init__(self, subscribe: bool, domain: str, account: str):
        self.subscribe = subscribe
        self.domain = domain
        self.account = account

    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_offset = builder.CreateString(self.domain)
        account_offset = builder.CreateString(self.account)

        PositionsSubscription.PositionsSubscriptionStart(builder)
        PositionsSubscription.AddDomain(builder, domain_offset)
        PositionsSubscription.AddAccount(builder, account_offset)
        positions_subscription = PositionsSubscription.PositionsSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, positions_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.PositionsSubscription)
        positions_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, positions_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)

        builder.Finish(request)
        return u, bytes(builder.Output())



# TODO

class ClientIssuedOptionsSubscription():
    def __init__(self, subscribe: bool, domain: str, account: str):
        self.subscribe = subscribe
        self.domain = domain
        self.account = account

    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_offset = builder.CreateString(self.domain)
        account_offset = builder.CreateString(self.account)

        IssuedOptionsSubscription.IssuedOptionsSubscriptionStart(builder)
        IssuedOptionsSubscription.AddDomain(builder, domain_offset)
        IssuedOptionsSubscription.AddAccount(builder, account_offset)
        issued_options_subscription = IssuedOptionsSubscription.IssuedOptionsSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, issued_options_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.IssuedOptionsSubscription)
        issued_options_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, issued_options_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)

        builder.Finish(request)
        return u, bytes(builder.Output())

class ClientTradeSubscription():
    def __init__(self, subscribe: bool, domain: str, market: str):
        self.subscribe = subscribe
        self.domain = domain
        self.market = market

    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_offset = builder.CreateString(self.domain)
        market_offset = builder.CreateString(self.market)

        TradeSubscription.TradeSubscriptionStart(builder)
        TradeSubscription.AddDomain(builder, domain_offset)
        TradeSubscription.AddMarket(builder, market_offset)
        trade_subscription = TradeSubscription.TradeSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, trade_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.TradeSubscription)
        trade_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, trade_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)

        builder.Finish(request)
        return u, bytes(builder.Output())


class ClientL2BookSubscription():
    def __init__(self, subscribe: bool, domain: str, market: str, levels: int = 10):
        self.subscribe = subscribe
        self.domain = domain
        self.market = market
        self.levels = levels

    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_offset = builder.CreateString(self.domain)
        market_offset = builder.CreateString(self.market)

        L2BookSubscription.L2BookSubscriptionStart(builder)
        L2BookSubscription.AddDomain(builder, domain_offset)
        L2BookSubscription.AddMarket(builder, market_offset)
        L2BookSubscription.AddNLevels(builder, self.levels)
        l2_book_subscription = L2BookSubscription.L2BookSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, l2_book_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.L2BookSubscription)
        l2_book_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, l2_book_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)

        builder.Finish(request)
        return u, bytes(builder.Output())





# TODO
class ClientLeaderboardSubscription():
    def __init__(self, subscribe: bool, domain: str):
        self.subscribe = subscribe
        self.domain = domain

    def to_bytes(self) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_offset = builder.CreateString(self.domain)

        LeaderboardSubscription.LeaderboardSubscriptionStart(builder)
        LeaderboardSubscription.AddDomain(builder, domain_offset)
        leaderboard_subscription = LeaderboardSubscription.LeaderboardSubscriptionEnd(builder)

        u = str(uuid.uuid4())
        print("UUID Leaderboard Subscription:", u)
        uuid_off = builder.CreateString(u)

        SubscriptionRequest.SubscriptionRequestStart(builder)
        SubscriptionRequest.AddUuid(builder, uuid_off)
        SubscriptionRequest.AddSubscribe(builder, self.subscribe)
        SubscriptionRequest.AddSubscription(builder, leaderboard_subscription)
        SubscriptionRequest.AddSubscriptionType(builder, Subscription.LeaderboardSubscription)
        leaderboard_subscription_request = SubscriptionRequest.SubscriptionRequestEnd(builder)

        ClientRequest.ClientRequestStart(builder)
        ClientRequest.AddRequestType(builder, ClientRequestUnion.SubscriptionRequest)
        ClientRequest.AddRequest(builder, leaderboard_subscription_request)
        request = ClientRequest.ClientRequestEnd(builder)

        builder.Finish(request)
        return u, bytes(builder.Output())