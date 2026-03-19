from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# open browser
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 15)

# 1️⃣ open login page
driver.get("http://127.0.0.1:8000/login")

# 2️⃣ enter login details
wait.until(EC.presence_of_element_located((By.NAME, "email"))).send_keys("reshmapal5131@gmail.com")
driver.find_element(By.NAME, "password").send_keys("123456")

# 3️⃣ click LOGIN button (IMPORTANT FIX)
driver.find_element(By.XPATH, "//button[contains(text(),'Login')]").click()

# 4️⃣ wait for dashboard textarea (means login success)
wait.until(EC.presence_of_element_located((By.NAME, "source_code")))

# 5️⃣ enter code
driver.find_element(By.NAME, "source_code").send_keys("print('Hello World')")

# 6️⃣ select languages
driver.find_element(By.NAME, "source_lang").send_keys("python")
driver.find_element(By.NAME, "target_lang").send_keys("java")

# 7️⃣ click convert
driver.find_element(By.XPATH, "//button[contains(text(),'Convert')]").click()

# 8️⃣ wait for output
wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "textarea")))
areas = driver.find_elements(By.TAG_NAME, "textarea")

# 9️⃣ check result
if len(areas) > 1:
    print("✅ FINAL TEST PASSED")
else:
    print("❌ TEST FAILED")

driver.quit()