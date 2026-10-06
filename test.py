from pydantic import BaseModel

class RetryContext(BaseModel):
    attempts_used: int = 0
    max_attempts: int = 3

    @property
    def can_retry(self) -> bool:
        return self.attempts_used < self.max_attempts

    @property
    def exhausted(self) -> bool:
        return self.attempts_used >= self.max_attempts

    def record_attempt(self) -> "RetryContext":
        return self.model_copy(
            update={"attempts_used": self.attempts_used + 1}
        )


retry = RetryContext()          # ✅ نمونه ساخت
retry = retry.record_attempt()  # ✅ فراخوانی متد

for _ in range(3):
    print()
    print(retry.attempts_used)
    print(retry.can_retry)
    print(retry.exhausted)
    print('_____________________')
    retry = retry.record_attempt()