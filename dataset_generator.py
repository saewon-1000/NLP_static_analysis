"""
Synthetic Embedded C Code Dataset Generator
의미 기반 정적 분석을 위한 임베디드 C 코드 데이터셋 생성
"""

import json
import random
from typing import List, Dict

class EmbeddedCDatasetGenerator:
    def __init__(self):
        self.dataset = []
        
    def generate_dataset(self, num_samples: int = 100) -> List[Dict]:
        """정상 코드와 위험 코드를 포함한 데이터셋 생성"""
        
        # 50% 정상, 50% 위험 코드
        for i in range(num_samples // 2):
            self.dataset.append(self._generate_safe_code(i))
            self.dataset.append(self._generate_dangerous_code(i))
        
        random.shuffle(self.dataset)
        return self.dataset
    
    def _generate_safe_code(self, idx: int) -> Dict:
        """정상적인 임베디드 C 코드 생성"""
        templates = [
            # 1. 안전한 버퍼 처리
            {
                "code": """void process_sensor_data(uint8_t *buffer, size_t len) {
    if (buffer == NULL || len == 0 || len > MAX_BUFFER_SIZE) {
        return;
    }
    
    for (size_t i = 0; i < len; i++) {
        sensor_data[i] = buffer[i];
    }
}""",
                "label": "safe",
                "category": "buffer_handling",
                "description": "Proper bounds checking and null pointer validation"
            },
            # 2. 안전한 인터럽트 처리
            {
                "code": """void UART_IRQHandler(void) {
    uint8_t data;
    
    if (UART->SR & UART_SR_RXNE) {
        data = UART->DR;
        
        if (rx_buffer_index < RX_BUFFER_SIZE) {
            rx_buffer[rx_buffer_index++] = data;
        } else {
            error_count++;
        }
    }
}""",
                "label": "safe",
                "category": "interrupt_handling",
                "description": "Safe interrupt handler with overflow protection"
            },
            # 3. 안전한 메모리 할당
            {
                "code": """int allocate_device_buffer(device_t *dev) {
    if (dev == NULL) {
        return -1;
    }
    
    dev->buffer = (uint8_t*)malloc(DEVICE_BUFFER_SIZE);
    if (dev->buffer == NULL) {
        return -1;
    }
    
    memset(dev->buffer, 0, DEVICE_BUFFER_SIZE);
    dev->buffer_size = DEVICE_BUFFER_SIZE;
    return 0;
}""",
                "label": "safe",
                "category": "memory_management",
                "description": "Proper memory allocation with error checking"
            },
            # 4. 안전한 포인터 연산
            {
                "code": """void read_flash_page(uint32_t page_addr, uint8_t *data, size_t len) {
    if (data == NULL || len == 0) {
        return;
    }
    
    if (page_addr >= FLASH_END_ADDR) {
        return;
    }
    
    uint32_t max_read = FLASH_END_ADDR - page_addr;
    size_t read_len = (len < max_read) ? len : max_read;
    
    memcpy(data, (void*)page_addr, read_len);
}""",
                "label": "safe",
                "category": "pointer_arithmetic",
                "description": "Safe flash memory read with boundary checks"
            },
            # 5. 안전한 타입 변환
            {
                "code": """uint16_t read_adc_value(void) {
    uint32_t raw_value = ADC->DR;
    
    // 12-bit ADC, ensure value is within range
    if (raw_value > 0xFFF) {
        raw_value = 0xFFF;
    }
    
    return (uint16_t)raw_value;
}""",
                "label": "safe",
                "category": "type_conversion",
                "description": "Safe type conversion with range validation"
            }
        ]
        
        template = random.choice(templates)
        return {
            "id": f"safe_{idx}",
            "code": template["code"],
            "label": template["label"],
            "category": template["category"],
            "description": template["description"],
            "vulnerability": None,
            "severity": "none"
        }
    
    def _generate_dangerous_code(self, idx: int) -> Dict:
        """의미적으로 위험한 임베디드 C 코드 생성 (Regex로는 탐지 어려움)"""
        templates = [
            # 1. 의미적 버퍼 오버플로우 (조건문은 있으나 논리 오류)
            {
                "code": """void process_uart_data(uint8_t *input, int len) {
    // 체크는 있지만 '<' 대신 '<='를 사용하여 off-by-one 오류
    if (input != NULL && len <= BUFFER_SIZE) {
        for (int i = 0; i <= len; i++) {  // 위험: i <= len
            uart_buffer[i] = input[i];
        }
    }
}""",
                "label": "dangerous",
                "category": "buffer_overflow",
                "description": "Off-by-one error in loop condition",
                "vulnerability": "Buffer overflow due to incorrect boundary condition (i <= len instead of i < len)",
                "severity": "high"
            },
            # 2. 경쟁 조건 (Race Condition)
            {
                "code": """volatile uint32_t shared_counter = 0;

void increment_counter(void) {
    // ISR과 main에서 동시 접근 가능
    uint32_t temp = shared_counter;
    temp++;
    shared_counter = temp;  // 위험: 원자성 없음
}""",
                "label": "dangerous",
                "category": "race_condition",
                "description": "Non-atomic operation on shared variable",
                "vulnerability": "Race condition: shared variable modified without atomic operation or critical section",
                "severity": "high"
            },
            # 3. 의미적 널 포인터 역참조
            {
                "code": """void configure_peripheral(device_config_t *config) {
    if (config->mode == MODE_ENABLED) {
        // config는 체크했지만 내부 포인터는 체크 안 함
        config->settings->baudrate = 115200;  // 위험: settings가 NULL일 수 있음
        config->settings->parity = PARITY_NONE;
    }
}""",
                "label": "dangerous",
                "category": "null_pointer",
                "description": "Unchecked nested pointer dereference",
                "vulnerability": "Null pointer dereference: config->settings not validated before use",
                "severity": "high"
            },
            # 4. 정수 오버플로우
            {
                "code": """void allocate_sensor_array(uint16_t num_sensors) {
    // num_sensors가 크면 오버플로우 발생
    uint16_t total_size = num_sensors * sizeof(sensor_t);  // 위험: 오버플로우
    
    sensor_array = (sensor_t*)malloc(total_size);
    if (sensor_array != NULL) {
        memset(sensor_array, 0, total_size);
    }
}""",
                "label": "dangerous",
                "category": "integer_overflow",
                "description": "Integer overflow in size calculation",
                "vulnerability": "Integer overflow: multiplication can overflow uint16_t, leading to small allocation",
                "severity": "critical"
            },
            # 5. 초기화되지 않은 변수 사용
            {
                "code": """int read_sensor_status(void) {
    int status;
    
    if (SENSOR_REG & SENSOR_READY) {
        status = SENSOR_REG_STATUS;
    }
    // else 분기에서 status 초기화 안 됨
    
    return status;  // 위험: 초기화 안 된 값 반환 가능
}""",
                "label": "dangerous",
                "category": "uninitialized_variable",
                "description": "Potentially uninitialized variable return",
                "vulnerability": "Uninitialized variable: status may be returned without initialization",
                "severity": "medium"
            },
            # 6. 시간 기반 논리 오류 (TOCTOU)
            {
                "code": """void write_to_device(uint8_t *data, size_t len) {
    if (device_ready()) {  // Check
        delay_ms(10);  // 지연 추가
        device_write(data, len);  // Use - 이 사이에 상태 변경 가능
    }
}""",
                "label": "dangerous",
                "category": "toctou",
                "description": "Time-of-check to time-of-use vulnerability",
                "vulnerability": "TOCTOU: device state may change between check and use",
                "severity": "medium"
            },
            # 7. 의미적 메모리 누수
            {
                "code": """void process_messages(void) {
    message_t *msg = allocate_message();
    
    if (msg->priority > PRIORITY_THRESHOLD) {
        handle_high_priority(msg);
        return;  // 위험: early return, msg 해제 안 됨
    }
    
    handle_normal_priority(msg);
    free_message(msg);
}""",
                "label": "dangerous",
                "category": "memory_leak",
                "description": "Memory leak on early return path",
                "vulnerability": "Memory leak: allocated message not freed on early return",
                "severity": "medium"
            },
            # 8. 잘못된 비트마스킹
            {
                "code": """void configure_gpio(uint8_t pin, uint8_t mode) {
    // 의도: 특정 핀만 설정하려 했으나 잘못된 비트 연산
    GPIO_CONFIG = GPIO_CONFIG | (mode << pin);  // 위험: 기존 비트 클리어 안 함
    // 올바른 방법: GPIO_CONFIG = (GPIO_CONFIG & ~(0x03 << pin)) | (mode << pin);
}""",
                "label": "dangerous",
                "category": "bit_manipulation",
                "description": "Incorrect bit masking operation",
                "vulnerability": "Bit manipulation error: existing bits not cleared before setting new value",
                "severity": "medium"
            },
            # 9. 부적절한 캐스팅
            {
                "code": """void set_timer_period(uint32_t period_us) {
    // 32비트를 16비트로 자르면서 상위 비트 손실
    TIMER_PERIOD = (uint16_t)period_us;  // 위험: 데이터 손실
    
    // period_us가 65535보다 크면 의도치 않은 동작
}""",
                "label": "dangerous",
                "category": "type_truncation",
                "description": "Type truncation leading to data loss",
                "vulnerability": "Type truncation: 32-bit value truncated to 16-bit without validation",
                "severity": "high"
            },
            # 10. 잘못된 포인터 산술
            {
                "code": """void copy_packet_data(packet_t *pkt) {
    uint8_t *src = pkt->data;
    uint8_t *dest = buffer;
    
    // pkt->length가 검증되지 않음
    for (int i = 0; i < pkt->length; i++) {
        *dest++ = *src++;  // 위험: dest 버퍼 경계 체크 없음
    }
}""",
                "label": "dangerous",
                "category": "pointer_arithmetic",
                "description": "Unchecked pointer arithmetic in loop",
                "vulnerability": "Buffer overflow: destination buffer bounds not validated",
                "severity": "high"
            }
        ]
        
        template = random.choice(templates)
        return {
            "id": f"dangerous_{idx}",
            "code": template["code"],
            "label": template["label"],
            "category": template["category"],
            "description": template["description"],
            "vulnerability": template["vulnerability"],
            "severity": template["severity"]
        }
    
    def save_dataset(self, filename: str = "embedded_c_dataset.json"):
        """데이터셋을 JSON 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.dataset, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Dataset saved: {filename}")
        print(f"  Total samples: {len(self.dataset)}")
        print(f"  Safe samples: {sum(1 for d in self.dataset if d['label'] == 'safe')}")
        print(f"  Dangerous samples: {sum(1 for d in self.dataset if d['label'] == 'dangerous')}")
        
        return filename

if __name__ == "__main__":
    generator = EmbeddedCDatasetGenerator()
    dataset = generator.generate_dataset(num_samples=100)
    generator.save_dataset("./embedded_c_dataset.json")
