"""โหลดค่าตั้งจาก config/default.yaml และความลับจาก .env

ทำไมแยก: ตัวเลขที่ปรับได้อยู่ใน yaml (เข้า git มีประวัติการแก้)
ส่วน API key อยู่ใน .env (ไม่เข้า git)
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "default.yaml"


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    """อ่าน yaml แล้วคืนเป็น dict

    TODO(ฉาก 1): ใช้ yaml.safe_load อ่านไฟล์
    """
    raise NotImplementedError


def load_secrets() -> dict:
    """อ่าน API key จาก .env

    TODO(ฉาก 5): ใช้ python-dotenv — ยังไม่ต้องใช้จนกว่าจะถึง testnet
    """
    raise NotImplementedError
