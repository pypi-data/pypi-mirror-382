import asyncio

from app.pojo.camera import CameraInfo
from app.pojo.device import DeviceInfo
from app.server.aiomysqlServer import MysqlServiceAsync
from app.server.aiosqlServer import SqlServerServiceAsync
from app.utils.concectUtils import is_ip_online, is_ip_online_async


async def process_camera(camera_info, sql_server):
    # 判断IP是否在线
    camera_info['cameraState'] = await is_ip_online_async(camera_info["ip"])
    #camera_info['cameraState'] = "1"
    # 查询设备信息
    device_info = await sql_server.fetch_device_by_MachineNo(camera_info["bind_device_code"])
    # 封装设备信息
    camera_info["device"] = DeviceInfo.new_DeviceInfo(device_info)
    # 封装摄像头信息
    return CameraInfo.new_camera(camera_info)

async def process_cameras(camera_info_list, sql_server):
    tasks = [process_camera(camera_info, sql_server) for camera_info in camera_info_list]
    camera_list = await asyncio.gather(*tasks)
    return camera_list


async def get_camrea_info_list():
    """
    获取所有的相机信息
    :return:
    """

    mysql_server = MysqlServiceAsync()
    sql_server = SqlServerServiceAsync()
    await mysql_server.init_pool()
    await sql_server.init_pool()
    camrea_info_list = await mysql_server.select_all_camrea_info()  # 获取到摄像头信息集合
    camera_list =await process_cameras(camrea_info_list, sql_server)
    # camera_list = []
    # for camera_info in camrea_info_list:
    #     camera_info['cameraState'] =  await is_ip_online_async(camera_info["ip"])  # 判断ip是否在线并设置状态
    #     device_info = await sql_server.fetch_device_by_MachineNo(camera_info["bind_device_code"])  # 通绑定的编码去查询设备数据
    #     camera_info["device"] = DeviceInfo.new_DeviceInfo(device_info)  # 将设备封装到实体类中在添加到camera_info中
    #     camera_list.append(CameraInfo.new_camera(camera_info))  # 将camera_info封装到实体类中，在添加到集合中
    await mysql_server.close_pool()
    await sql_server.close_pool()
    return camera_list

if __name__ == '__main__':
    camrea_info_list = asyncio.run(get_camrea_info_list())
    print(camrea_info_list)