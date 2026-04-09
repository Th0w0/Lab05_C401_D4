import os
import sys

# Đảm bảo đường dẫn import trong project không bị lỗi
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.toolsCS import demo
except ImportError as e:
    print(f"Lỗi khởi tạo module: {e}")
    sys.exit(1)

if __name__ == "__main__":
    print("🚀 Đang khởi động VinFast Smart Assistant 2026 (Local+Fallback)...")
    demo.launch(share=True)
