import time
from dataclasses import dataclass
from collections import deque

@dataclass
class Request:
    user_id: str
    req_id: int

@dataclass
class Token:
    used: float
    last_used_at: float
    

dead_letter_queue = deque()
    

class TokenBucket:
    def __init__(self, fill_rate: float, capacity: int):
        self.fill_rate = fill_rate
        self.capacity = capacity
        self.__bucket = dict()
    
    # Public API
    def update_fill_rate(self, fill_rate: bool) -> None:
        self.fill_rate = fill_rate
        
    # Public API
    def update_capacity(self, capacity: int) -> None:
        self.capacity = capacity
    
    # Internal
    def is_request_allowed(self, request: Request) -> bool:
        time_now = time.time()
        
        if request.user_id not in self.__bucket:
            self.__bucket[request.user_id] = Token(used=0, last_used_at=time_now)
        
        last_successful_token: Token = self.__bucket[request.user_id]
        elapsed = (time_now - last_successful_token.last_used_at)
        # LOG
        print(f'Elapsed time: {elapsed}')
        refill = self.fill_rate * elapsed
        new_token = min(self.capacity, last_successful_token.used + refill)
        print(f'Current tokens: {new_token}')
        allowed = new_token > 1
        
        if allowed:
            new_token -= 1
            self.__bucket[request.user_id] = Token(new_token, time_now)
        else:
            dead_letter_queue.append(req)
            
        return allowed
    
    
if __name__ == '__main__':
    rate_limiter_token_bucket = TokenBucket(5, 10)
    user_id = "usr_123"
    
    for i in range(6):
        req = Request(user_id, i)
        if rate_limiter_token_bucket.is_request_allowed(req):
            print(f'Request {req.req_id} allowed')
            # forward_request(server_id, req)
        else:
            print(f'Request {req.req_id} rejected')
            # send(client_id, response)
        print('-' * 10)
        time.sleep(0.1)
        
    # Reprocess dlq
    print(f'Rejected requests: {dead_letter_queue}')