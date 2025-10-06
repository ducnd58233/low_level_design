"""
1 Question
- Design and implement a Rate Limiter that control the rate of traffic sent by a client. 
It should limits the number of client requests allowed to be sent over a specified period. 
If the request count exceeds the threshold, all the excess requests should be blocked.
- Example:
+ A user can write no more than 2 posts per second.
+ You can create a maximum of 10 accounts per day from the same IP address.
+ You can claim rewards no more than 5 times per week from the same account

2 Clarify question
- 1. What kind of rate limiter are we designing, client-side or server-side? (Answer: server-side) 
- 2. What property should the rate limiter use to throttle requests. E.g.: IP, user ID, or other properties? (Answer: should be flexible enough to support different configurations)
- 3. Is there any specific rate limiting algorithm I should implement? (Answer: you should list out a few options and their pros and cons, but for the interest of time just pick one for implementation)
- 4. Is the rate limiter a separate service or should it implemented as part of server application code? (Answer: design decision is up to you)
- 5. Do we inform users that their requests are throttled (Answer: Yes)
- 6. Do we support burst of requests (Answer: Yes)

3 Analyze the problem
3.1 Key challenges:
- Accurately limit excessive requests.
- Low latency: the rate limiter should not slow down API response time.
- Use as little memory as possible.
- Exception handling: show clear exception to client when their requests are being throttled.
- Fault tolerance: if the rate limiter has problems, it does not affect the entire system.

3.2 Common algorithms:
- Token bucket
- Leaky bucket
- Fixed window
- Sliding window counter
"""

import time
import threading
from abc import ABC, abstractmethod
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

class RateLimiter(ABC):
    # Public API
    @abstractmethod
    def update_fill_rate(self, fill_rate: bool) -> None:
        raise NotImplementedError
        
    # Public API
    @abstractmethod
    def update_capacity(self, capacity: int) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def is_request_allowed(self, request: Request) -> tuple[bool, str]:
        raise NotImplementedError
    
    

class TokenBucket(RateLimiter):
    def __init__(self, fill_rate: float, capacity: int, key_func=lambda req: req.user_id):
        self.fill_rate = fill_rate
        self.capacity = capacity
        self.key_func = key_func
        self.__bucket = dict()
        self.lock = threading.Lock()
    
    # Public API
    def update_fill_rate(self, fill_rate: bool) -> None:
        self.fill_rate = fill_rate
        
    # Public API
    def update_capacity(self, capacity: int) -> None:
        self.capacity = capacity
    
    # Internal
    def is_request_allowed(self, request: Request) -> tuple[bool, str]:
        key = self.key_func(request)
        time_now = time.time()
        
        with self.lock:
            if key not in self.__bucket:
                self.__bucket[key] = Token(used=0, last_used_at=time_now)
            
            last_successful_token: Token = self.__bucket[key]
            elapsed = (time_now - last_successful_token.last_used_at)
            # LOG
            print(f'Elapsed time: {elapsed}')
            refill = self.fill_rate * elapsed
            new_token = min(self.capacity, last_successful_token.used + refill)
            print(f'Current tokens: {new_token}')
            allowed = new_token > 1
            
            if not allowed:
                dead_letter_queue.append(request)
                return False, "Rate limit exceed"
                
            new_token -= 1
            self.__bucket[key] = Token(new_token, time_now)
                
            return True, "Allowed"
    
def simulate_user(rate_limiter: RateLimiter, user_id: str, num_requests: int):
    for i in range(num_requests):
        req = Request(user_id, i)
        _, msg = rate_limiter.is_request_allowed(req)
        print(f'[User {user_id}] Request {req.req_id}: {msg}')
        print('-' * 10)
        
        time.sleep(0.05)

if __name__ == '__main__':
    rate_limiter_token_bucket = TokenBucket(5, 10)
    threads: list[threading.Thread] = []
    
    for uid in ['usr_1', 'usr_2','usr_3']:
        t = threading.Thread(target=simulate_user, args=(rate_limiter_token_bucket, uid, 15))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
        
    # Reprocess dlq
    print(f'Rejected requests: {dead_letter_queue}')