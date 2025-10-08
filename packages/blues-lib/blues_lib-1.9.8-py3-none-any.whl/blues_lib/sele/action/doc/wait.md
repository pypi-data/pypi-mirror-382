## wait机制
### 强制等待
不做任何判断，直接设置固定等待时间
```py
time.sleep(5)
```

### 隐式等待
全局性设置一个最大等待时间，在任何时候使用`find_element[s]`查找元素时，都会等待超过最大时间后才结束
- 有时候增加了不必要耗时，例如：我只想立即判断某个元素是否已被正确移除，并不需要等待时间
```py
this.driver.implicitly_wait(30)
```

### 显式等待
通过函数判断某个条件是否满足，满足立即执行，还要设置一个最大等待时间，超时未满足条件，失败。
```py
wait_func = expected_conditions.presence_of_element_located((By.CSS_SELECTOR,'#name'))
WebDriverWait(self.driver,timeout=30).until(wait_func)
```