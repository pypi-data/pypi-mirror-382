"""
Module cung cấp các dependency cho MCP (Microservice Connection Provider).

Module này chứa các dependency và factory functions để inject các MCP services
vào các route handlers. MCP services cho phép kết nối đến các cơ sở dữ liệu
và services khác từ microservice hiện tại.
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from cores.component.mcp.mcp_factory import MCPServiceType, mcp_manager
from cores.interface.mcp_interface import IMCPService, MCPConnectionInfo


async def get_mcp_service(
    service_name: str = "default",
    service_type: MCPServiceType = MCPServiceType.MYSQL,
) -> IMCPService:
    """
    Dependency để inject MCP service.

    Trả về một MCP service với cấu hình mặc định.

    Args:
        service_name: Tên của service, mặc định là "default"
        service_type: Loại service, mặc định là MYSQL

    Returns:
        IMCPService instance đã được khởi tạo
    """
    return await mcp_manager.get_service(service_name, service_type)


async def get_mysql_mcp_service(
    service_name: str = "mysql_default",
) -> IMCPService:
    """
    Dependency để inject MySQL MCP service.

    Trả về một MySQL MCP service với cấu hình mặc định.

    Args:
        service_name: Tên của MySQL service, mặc định là "mysql_default"

    Returns:
        IMCPService instance đã được khởi tạo cho MySQL
    """
    return await mcp_manager.get_mysql_service(service_name)


async def get_custom_mcp_service(
    service_name: str,
    service_type: MCPServiceType,
    connection_info: MCPConnectionInfo | None = None,
) -> IMCPService:
    """
    Dependency để inject custom MCP service với connection riêng.

    Cho phép tạo một MCP service với cấu hình tùy chỉnh.

    Args:
        service_name: Tên của service
        service_type: Loại service (MYSQL, POSTGRESQL, etc.)
        connection_info: Thông tin kết nối, None để sử dụng cấu hình mặc định

    Returns:
        IMCPService instance đã được khởi tạo với cấu hình tùy chỉnh
    """
    return await mcp_manager.get_service(
        service_name=service_name,
        service_type=service_type,
        auto_initialize=True,
        connection_info=connection_info,
    )


# Type aliases for easier usage
MCPService = Annotated[IMCPService, Depends(get_mcp_service)]
MySQLMCPService = Annotated[IMCPService, Depends(get_mysql_mcp_service)]


# Factory functions for custom dependencies
def create_mysql_dependency(service_name: str = "mysql_custom") -> Callable:
    """
    Factory để tạo dependency cho MySQL service với tên tùy chỉnh.

    Args:
        service_name: Tên của MySQL service, mặc định là "mysql_custom"

    Returns:
        Dependency callable để sử dụng với FastAPI Depends
    """

    async def _get_mysql_service() -> IMCPService:
        return await mcp_manager.get_mysql_service(service_name)

    return Depends(_get_mysql_service)


def create_custom_dependency(
    service_name: str,
    service_type: MCPServiceType = MCPServiceType.MYSQL,
    connection_info: MCPConnectionInfo | None = None,
) -> Callable:
    """
    Factory để tạo dependency cho service với cấu hình tùy chỉnh.

    Args:
        service_name: Tên của service
        service_type: Loại service, mặc định là MYSQL
        connection_info: Thông tin kết nối, None để sử dụng cấu hình mặc định

    Returns:
        Dependency callable để sử dụng với FastAPI Depends
    """

    async def _get_custom_service() -> IMCPService:
        return await mcp_manager.get_service(
            service_name=service_name,
            service_type=service_type,
            auto_initialize=True,
            connection_info=connection_info,
        )

    return Depends(_get_custom_service)
