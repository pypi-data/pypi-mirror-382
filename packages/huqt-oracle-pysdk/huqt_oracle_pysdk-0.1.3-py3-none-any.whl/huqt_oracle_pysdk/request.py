import uuid
import flatbuffers

from .fbs_gen.client import (
    UnaryRequest,
    SetSessionRequest,
    RevokeSessionRequest,
    ClientRequest,
    AddOrderRequest,
    CancelOrderRequest,
    DepositRequest,
    WithdrawRequest,
    ConversionRequest,
    ExerciseOptionRequest,
    IssueOptionRequest,
)

from .fbs_gen.client.UnaryRequestUnion import UnaryRequestUnion
from .fbs_gen.client.ClientRequestUnion import ClientRequestUnion
from .fbs_gen.client.Tif import Tif
from .fbs_gen.client.OrderType import OrderType
from .fbs_gen.gateway.Side import Side

class ClientAddOrderRequest:
    def __init__(self,
                 domain: str,
                 market: str,
                 side: Side,
                 px: int,
                 sz: int,
                 collateral: int,
                 order_type: OrderType,
                 tif: Tif):
        self.domain = domain
        self.market = market
        self.side = side
        self.px = px
        self.side = side
        self.sz = sz
        self.collateral = collateral
        self.order_type = order_type
        self.tif = tif
    
    def to_bytes(self, account: str) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_off = builder.CreateString(self.domain)
        market_off = builder.CreateString(self.market)

        # AddOrderRequest
        AddOrderRequest.AddOrderRequestStart(builder)
        AddOrderRequest.AddOrderRequestAddDomain(builder, domain_off)
        AddOrderRequest.AddOrderRequestAddMarket(builder, market_off)
        AddOrderRequest.AddOrderRequestAddSide(builder, self.side)
        AddOrderRequest.AddOrderRequestAddPx(builder, self.px)
        AddOrderRequest.AddOrderRequestAddSz(builder, self.sz)
        AddOrderRequest.AddOrderRequestAddCollateral(builder, self.collateral)
        AddOrderRequest.AddOrderRequestAddOrderType(builder, self.order_type)
        AddOrderRequest.AddOrderRequestAddTif(builder, self.tif)
        add_order_req = AddOrderRequest.AddOrderRequestEnd(builder)

        # UnaryRequest
        account_off = builder.CreateString(account)
        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)
        UnaryRequest.UnaryRequestStart(builder)
        UnaryRequest.UnaryRequestAddUuid(builder, uuid_off)
        UnaryRequest.UnaryRequestAddAccount(builder, account_off)
        UnaryRequest.UnaryRequestAddRequest(builder, add_order_req)
        UnaryRequest.UnaryRequestAddRequestType(builder, UnaryRequestUnion.AddOrderRequest)
        add_order_unary_req = UnaryRequest.UnaryRequestEnd(builder)

        # ClientRequest (wrap the union)
        ClientRequest.ClientRequestStart(builder)
        ClientRequest.ClientRequestAddRequest(builder, add_order_unary_req)
        ClientRequest.ClientRequestAddRequestType(builder, ClientRequestUnion.UnaryRequest)
        req = ClientRequest.ClientRequestEnd(builder)
        builder.Finish(req)

        return u, bytes(builder.Output())

class ClientCancelOrderRequest:
    def __init__(self, domain: str, market: str, order_id: int):
        self.domain = domain
        self.market = market
        self.order_id = order_id

    def to_bytes(self, account: str) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_off = builder.CreateString(self.domain)
        market_off = builder.CreateString(self.market)

        # CancelOrderRequest
        CancelOrderRequest.CancelOrderRequestStart(builder)
        CancelOrderRequest.CancelOrderRequestAddDomain(builder, domain_off)
        CancelOrderRequest.CancelOrderRequestAddMarket(builder, market_off)
        CancelOrderRequest.CancelOrderRequestAddOid(builder, self.order_id)
        cancel_order_req = CancelOrderRequest.CancelOrderRequestEnd(builder)

        # UnaryRequest
        account_off = builder.CreateString(account)
        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)
        UnaryRequest.UnaryRequestStart(builder)
        UnaryRequest.UnaryRequestAddUuid(builder, uuid_off)
        UnaryRequest.UnaryRequestAddAccount(builder, account_off)
        UnaryRequest.UnaryRequestAddRequest(builder, cancel_order_req)
        UnaryRequest.UnaryRequestAddRequestType(builder, UnaryRequestUnion.CancelOrderRequest)
        cancel_order_unary_req = UnaryRequest.UnaryRequestEnd(builder)

        # ClientRequest (wrap the union)
        ClientRequest.ClientRequestStart(builder)
        ClientRequest.ClientRequestAddRequest(builder, cancel_order_unary_req)
        ClientRequest.ClientRequestAddRequestType(builder, ClientRequestUnion.UnaryRequest)
        req = ClientRequest.ClientRequestEnd(builder)
        builder.Finish(req)

        return u, bytes(builder.Output())

class ClientDepositRequest:
    def __init__(self, domain: str, symbol: str, amount: int):
        self.domain = domain
        self.symbol = symbol
        self.amount = amount
    
    def to_bytes(self, account: str) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_off = builder.CreateString(self.domain)
        symbol_off = builder.CreateString(self.symbol)

        # DepositRequest
        DepositRequest.DepositRequestStart(builder)
        DepositRequest.DepositRequestAddDomain(builder, domain_off)
        DepositRequest.DepositRequestAddSymbol(builder, symbol_off)
        DepositRequest.DepositRequestAddAmount(builder, self.amount)
        deposit_req = DepositRequest.DepositRequestEnd(builder)

        # UnaryRequest
        account_off = builder.CreateString(account)
        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)
        UnaryRequest.UnaryRequestStart(builder)
        UnaryRequest.UnaryRequestAddUuid(builder, uuid_off)
        UnaryRequest.UnaryRequestAddAccount(builder, account_off)
        UnaryRequest.UnaryRequestAddRequest(builder, deposit_req)
        UnaryRequest.UnaryRequestAddRequestType(builder, UnaryRequestUnion.DepositRequest)
        deposit_unary_req = UnaryRequest.UnaryRequestEnd(builder)

        # ClientRequest (wrap the union)
        ClientRequest.ClientRequestStart(builder)
        ClientRequest.ClientRequestAddRequest(builder, deposit_unary_req)
        ClientRequest.ClientRequestAddRequestType(builder, ClientRequestUnion.UnaryRequest)
        req = ClientRequest.ClientRequestEnd(builder)
        builder.Finish(req)

        return u, bytes(builder.Output())

class ClientWithdrawRequest:
    def __init__(self, domain: str, symbol: str, amount: int):
        self.domain = domain
        self.symbol = symbol
        self.amount = amount
    
    def to_bytes(self, account: str) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_off = builder.CreateString(self.domain)
        symbol_off = builder.CreateString(self.symbol)

        # WithdrawRequest
        WithdrawRequest.WithdrawRequestStart(builder)
        WithdrawRequest.WithdrawRequestAddDomain(builder, domain_off)
        WithdrawRequest.WithdrawRequestAddSymbol(builder, symbol_off)
        WithdrawRequest.WithdrawRequestAddAmount(builder, self.amount)
        withdraw_req = WithdrawRequest.WithdrawRequestEnd(builder)

        # UnaryRequest
        account_off = builder.CreateString(account)
        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)
        UnaryRequest.UnaryRequestStart(builder)
        UnaryRequest.UnaryRequestAddUuid(builder, uuid_off)
        UnaryRequest.UnaryRequestAddAccount(builder, account_off)
        UnaryRequest.UnaryRequestAddRequest(builder, withdraw_req)
        UnaryRequest.UnaryRequestAddRequestType(builder, UnaryRequestUnion.WithdrawRequest)
        withdraw_unary_req = UnaryRequest.UnaryRequestEnd(builder)

        # ClientRequest (wrap the union)
        ClientRequest.ClientRequestStart(builder)
        ClientRequest.ClientRequestAddRequest(builder, withdraw_unary_req)
        ClientRequest.ClientRequestAddRequestType(builder, ClientRequestUnion.UnaryRequest)
        req = ClientRequest.ClientRequestEnd(builder)
        builder.Finish(req)

        return u, bytes(builder.Output())

class ClientConversionRequest:
    def __init__(self, domain: str, conversion: str, size: int):
        self.domain = domain
        self.conversion = conversion
        self.size = size
    
    def to_bytes(self, account: str) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_off = builder.CreateString(self.domain)
        conversion_off = builder.CreateString(self.conversion)

        # ConversionRequest
        ConversionRequest.ConversionRequestStart(builder)
        ConversionRequest.ConversionRequestAddDomain(builder, domain_off)
        ConversionRequest.ConversionRequestAddConversion(builder, conversion_off)
        ConversionRequest.ConversionRequestAddMult(builder, self.size)
        conversion_req = ConversionRequest.ConversionRequestEnd(builder)

        # UnaryRequest
        account_off = builder.CreateString(account)
        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)
        UnaryRequest.UnaryRequestStart(builder)
        UnaryRequest.UnaryRequestAddUuid(builder, uuid_off)
        UnaryRequest.UnaryRequestAddAccount(builder, account_off)
        UnaryRequest.UnaryRequestAddRequest(builder, conversion_req)
        UnaryRequest.UnaryRequestAddRequestType(builder, UnaryRequestUnion.ConversionRequest)
        conversion_unary_req = UnaryRequest.UnaryRequestEnd(builder)

        # ClientRequest (wrap the union)
        ClientRequest.ClientRequestStart(builder)
        ClientRequest.ClientRequestAddRequest(builder, conversion_unary_req)
        ClientRequest.ClientRequestAddRequestType(builder, ClientRequestUnion.UnaryRequest)
        req = ClientRequest.ClientRequestEnd(builder)
        builder.Finish(req)

        return u, bytes(builder.Output())

class ClientExerciseOptionRequest:
    def __init__(self, domain: str, name: str, size: int):
        self.domain = domain
        self.name = name
        self.size = size
    
    def to_bytes(self, account: str) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_off = builder.CreateString(self.domain)
        name_off = builder.CreateString(self.name)

        # ExerciseOptionRequest
        ExerciseOptionRequest.ExerciseOptionRequestStart(builder)
        ExerciseOptionRequest.ExerciseOptionRequestAddDomain(builder, domain_off)
        ExerciseOptionRequest.ExerciseOptionRequestAddName(builder, name_off)
        ExerciseOptionRequest.ExerciseOptionRequestAddAmount(builder, self.size)
        exercise_req = ExerciseOptionRequest.ExerciseOptionRequestEnd(builder)

        # UnaryRequest
        account_off = builder.CreateString(account)
        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)
        UnaryRequest.UnaryRequestStart(builder)
        UnaryRequest.UnaryRequestAddUuid(builder, uuid_off)
        UnaryRequest.UnaryRequestAddAccount(builder, account_off)
        UnaryRequest.UnaryRequestAddRequest(builder, exercise_req)
        UnaryRequest.UnaryRequestAddRequestType(builder, UnaryRequestUnion.ExerciseOptionRequest)
        exercise_unary_req = UnaryRequest.UnaryRequestEnd(builder)

        # ClientRequest (wrap the union)
        ClientRequest.ClientRequestStart(builder)
        ClientRequest.ClientRequestAddRequest(builder, exercise_unary_req)
        ClientRequest.ClientRequestAddRequestType(builder, ClientRequestUnion.UnaryRequest)
        req = ClientRequest.ClientRequestEnd(builder)
        builder.Finish(req)

        return u, bytes(builder.Output())

class ClientIssueOptionRequest:
    def __init__(self, domain: str, name: str, size: int):
        self.domain = domain
        self.name = name
        self.size = size
    
    def to_bytes(self, account: str) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_off = builder.CreateString(self.domain)
        name_off = builder.CreateString(self.name)

        # IssueOptionRequest
        IssueOptionRequest.IssueOptionRequestStart(builder)
        IssueOptionRequest.IssueOptionRequestAddDomain(builder, domain_off)
        IssueOptionRequest.IssueOptionRequestAddName(builder, name_off)
        IssueOptionRequest.IssueOptionRequestAddAmount(builder, self.size)
        issue_req = IssueOptionRequest.IssueOptionRequestEnd(builder)

        # UnaryRequest
        account_off = builder.CreateString(account)
        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)
        UnaryRequest.UnaryRequestStart(builder)
        UnaryRequest.UnaryRequestAddUuid(builder, uuid_off)
        UnaryRequest.UnaryRequestAddAccount(builder, account_off)
        UnaryRequest.UnaryRequestAddRequest(builder, issue_req)
        UnaryRequest.UnaryRequestAddRequestType(builder, UnaryRequestUnion.IssueOptionRequest)
        issue_unary_req = UnaryRequest.UnaryRequestEnd(builder)

        # ClientRequest (wrap the union)
        ClientRequest.ClientRequestStart(builder)
        ClientRequest.ClientRequestAddRequest(builder, issue_unary_req)
        ClientRequest.ClientRequestAddRequestType(builder, ClientRequestUnion.UnaryRequest)
        req = ClientRequest.ClientRequestEnd(builder)
        builder.Finish(req)

        return u, bytes(builder.Output())

class ClientSetSessionRequest:
    def __init__(self,
                 domain: str):
        self.domain = domain

    def to_bytes(self, account: str) -> tuple[str, bytes]:
        builder = flatbuffers.Builder()
        domain_off = builder.CreateString(self.domain)
        account_off = builder.CreateString(account)

        account_off = builder.CreateString(account)
        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)
        SetSessionRequest.SetSessionRequestStart(builder)
        SetSessionRequest.SetSessionRequestAddUuid(builder, uuid_off)
        SetSessionRequest.SetSessionRequestAddDomain(builder, domain_off)
        SetSessionRequest.SetSessionRequestAddAccount(builder, account_off)
        set_session_unary_req = SetSessionRequest.SetSessionRequestEnd(builder)

        # ClientRequest (wrap the union)
        ClientRequest.ClientRequestStart(builder)
        ClientRequest.ClientRequestAddRequest(builder, set_session_unary_req)
        ClientRequest.ClientRequestAddRequestType(builder, ClientRequestUnion.SetSessionRequest)
        req = ClientRequest.ClientRequestEnd(builder)
        builder.Finish(req)

        return u, bytes(builder.Output())

class ClientRevokeSessionRequest:
    def to_bytes() -> tuple[str, bytes]:
        builder = flatbuffers.Builder()

        u = str(uuid.uuid4())
        uuid_off = builder.CreateString(u)
        RevokeSessionRequest.RevokeSessionRequestStart(builder)
        RevokeSessionRequest.RevokeSessionRequestAddUuid(builder, uuid_off)
        revoke_session_unary_req = RevokeSessionRequest.RevokeSessionRequestEnd(builder)

        # ClientRequest (wrap the union)
        ClientRequest.ClientRequestStart(builder)
        ClientRequest.ClientRequestAddRequest(builder, revoke_session_unary_req)
        ClientRequest.ClientRequestAddRequestType(builder, ClientRequestUnion.RevokeSessionRequest)
        req = ClientRequest.ClientRequestEnd(builder)
        builder.Finish(req)

        return u, bytes(builder.Output())