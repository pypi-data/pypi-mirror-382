import requests
import logging
from decimal import Decimal, InvalidOperation
from typing import Union


class OPTools:

    @staticmethod
    def toDecimal(value, precision: int = None):
        """将数值转换为Decimal类型

        Args:
            value: 需要转换的数值
            precision: 精度,如果不指定则保持原始精度

        Returns:
            Decimal: 转换后的Decimal对象
        """
        if precision is None:
            return Decimal(str(value))
        return Decimal(f"{value:.{precision}f}")

    @staticmethod
    def ensure_decimal(value: Union[float, int, str, Decimal]) -> Decimal:
        """确保值被转换为Decimal类型

        Args:
            value: 需要转换的数值，可以是float、int、str或Decimal

        Returns:
            Decimal: 转换后的Decimal对象

        Raises:
            ValueError: 当值无法转换为Decimal时
        """
        if value is None:
            raise ValueError("Cannot convert None to Decimal")

        if isinstance(value, Decimal):
            return value

        try:
            return Decimal(str(value))
        except (ValueError, TypeError, InvalidOperation) as e:
            logger = logging.getLogger(__name__)
            logger.error(
                f"Failed to convert {value} (type: {type(value)}) to Decimal: {e}"
            )
            raise ValueError(f"Cannot convert {value} to Decimal: {e}")

    @staticmethod
    def safe_decimal_multiply(
        decimal_value: Decimal, multiplier: Union[float, int, Decimal]
    ) -> Decimal:
        """安全地将Decimal值与其他数值类型相乘

        Args:
            decimal_value: Decimal类型的被乘数
            multiplier: 乘数，可以是float、int或Decimal

        Returns:
            Decimal: 乘法运算的结果

        Raises:
            ValueError: 当输入值无法处理时
        """
        if not isinstance(decimal_value, Decimal):
            raise ValueError(
                f"First argument must be Decimal, got {type(decimal_value)}"
            )

        try:
            multiplier_decimal = OPTools.ensure_decimal(multiplier)
            return decimal_value * multiplier_decimal
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to multiply {decimal_value} by {multiplier}: {e}")
            raise ValueError(f"Decimal multiplication failed: {e}")

    @staticmethod
    def safe_decimal_add(
        decimal_value: Decimal, addend: Union[float, int, Decimal]
    ) -> Decimal:
        """安全地将Decimal值与其他数值类型相加

        Args:
            decimal_value: Decimal类型的被加数
            addend: 加数，可以是float、int或Decimal

        Returns:
            Decimal: 加法运算的结果
        """
        if not isinstance(decimal_value, Decimal):
            raise ValueError(
                f"First argument must be Decimal, got {type(decimal_value)}"
            )

        try:
            addend_decimal = OPTools.ensure_decimal(addend)
            return decimal_value + addend_decimal
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to add {addend} to {decimal_value}: {e}")
            raise ValueError(f"Decimal addition failed: {e}")

    @staticmethod
    def safe_decimal_subtract(
        decimal_value: Decimal, subtrahend: Union[float, int, Decimal]
    ) -> Decimal:
        """安全地从Decimal值中减去其他数值类型

        Args:
            decimal_value: Decimal类型的被减数
            subtrahend: 减数，可以是float、int或Decimal

        Returns:
            Decimal: 减法运算的结果
        """
        if not isinstance(decimal_value, Decimal):
            raise ValueError(
                f"First argument must be Decimal, got {type(decimal_value)}"
            )

        try:
            subtrahend_decimal = OPTools.ensure_decimal(subtrahend)
            return decimal_value - subtrahend_decimal
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to subtract {subtrahend} from {decimal_value}: {e}")
            raise ValueError(f"Decimal subtraction failed: {e}")

    @staticmethod
    def send_feishu_notification(webhook, message):
        if webhook:
            headers = {"Content-Type": "application/json"}
            data = {"msg_type": "text", "content": {"text": message}}
            response = requests.post(webhook, headers=headers, json=data)
            if response.status_code != 200:
                # self.logger.debug("飞书通知发送成功")
                raise Exception(f"飞书通知发送失败: {response.text} {webhook}")
