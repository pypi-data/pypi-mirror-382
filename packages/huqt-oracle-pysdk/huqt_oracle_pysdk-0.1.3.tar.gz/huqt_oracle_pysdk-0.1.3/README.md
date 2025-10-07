# avaliable endpoints for the 'OracleClient' object

## read states endpoints, all sync:
get_self_open_orders
get_self_positions
get_self_recent_fills
get_book
get_recent_trades
get_oracle_metadata
get_domain_metadata
get_self_pending_orders
get_self_pending_requests

## write states (sending ws requests to the server), all async:
place_limit_order
place_market_order
cancel_order
deposit
withdraw
convert
issue_option
exercise_option

TODO