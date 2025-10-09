
import asyncio
import os
import sys
import platform
import threading
import fibre
import mwdrive
from . import config, enums, rich_text, utils

def print_banner():
    print('官方网站(Website): https://www.cyberbeast.cn')
    print('用户手册(User Manual): https://cyberbeast.feishu.cn/docx/N3SMd4QyRobzHkx3wP3cT1qXnpf')
    print('协议手册(Protocol Manual): https://cyberbeast.feishu.cn/docx/BPnQd8reEotLWVxqHFNc9qYZnKh')

    print()
    print('请连接您的驱动器')
    print('输入help()获取操作帮助, exit退出')
    print('Please connect your MWDrive')
    print('You can also type help() or exit')

def print_help(args, have_devices):
    print('')
    if have_devices:
        print('连接到 {} 并打开电源, 然后会出现下述提示:'.format(args.path))
        print('  "Connected to MWDrive [serial number] as mdrv0"')
        print('')
        print('连接成功后, 输入"mdrv0."然后按<TAB>键可以查看所有可用参数/方法')
        print('')
        print('Connect your MWDrive to {} and power it up.'.format(args.path))
        print('After that, the following message should appear:')
        print('  "Connected to MWDrive [serial number] as mdrv0"')
        print('')
        print('Once the MWDrive is connected, type "mdrv0." and press <tab>')
        print('This will present you with all the properties that you can reference')
    else:
        print('输入"mdrv0."然后按<TAB>键可以查看所有可用参数/方法')
        print('Type "mdrv0." and press <tab>')
        print('This will present you with all the properties that you can reference')
    print('')
    print('例如: "mdrv0.axis0.encoder.pos_estimate"可以查看轴0的编码器位置')
    print('"mdrv0.axis0.controller.input_pos = 0.5" 可以让轴0转动到0.5圈位置')
    print('请注意, 力矩的单位是Nm, 速度的单位是圈/秒(电机转子侧), 位置的单位是圈(电机转子侧)')
    print('')
    print('For example: "mdrv0.axis0.encoder.pos_estimate"')
    print('will print the current encoder position on axis 0')
    print('and "mdrv0.axis0.controller.input_pos = 0.5"')
    print('will send axis 0 to 0.5 turns')
    print('')


interactive_variables = {}
discovered_devices = []

def benchmark(mdrv):
    import time

    async def measure_async():
        start = time.monotonic()
        futures = [mdrv.vbus_voltage for i in range(1000)]
#        data = [await f for f in futures]
#        print("took " + str(time.monotonic() - start) + " seconds. Average is " + str(sum(data) / len(data)))

    fibre.libfibre.libfibre.loop.call_soon_threadsafe(lambda: asyncio.ensure_future(measure_async()))

class ShellVariables():
    mwdrive = mwdrive
    devices = []
    config = config.MachineConfig()

    @staticmethod
    def apply():
        ShellVariables.config.apply(ShellVariables.devices)

    @staticmethod
    def status():
        rich_text.print_rich_text(ShellVariables.config.format_status(ShellVariables.devices))

    @staticmethod
    def calibrate():
        ShellVariables.config.calibrate(ShellVariables.devices)

def _import_from(source):
    return {
        k: getattr(source, k)
        for k in dir(source)
        if not k.startswith("_")
    }

def _wrap_async(func):
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

def launch_shell(args, logger):
    """
    Launches an interactive python or IPython command line
    interface.
    As MDrives are connected they are made available as
    "mdrv0", "mdrv1", ...
    """

    interactive_variables = {
        'start_liveplotter': utils.start_liveplotter,
        'dump_errors': utils.dump_errors,
        'benchmark': benchmark,
        'oscilloscope_dump': utils.oscilloscope_dump,
        'dump_interrupts': utils.dump_interrupts,
        'dump_threads': utils.dump_threads,
        'dump_dma': utils.dump_dma,
        'dump_timing': utils.dump_timing,
        'ram_osci_config': _wrap_async(utils.ram_osci_config),
        'ram_osci_trigger': utils.ram_osci_trigger,
        'ram_osci_download': _wrap_async(utils.ram_osci_download),
        'ram_osci_run': _wrap_async(utils.ram_osci_run),
        'BulkCapture': utils.BulkCapture,
        'step_and_plot': utils.step_and_plot,
        'calculate_thermistor_coeffs': utils.calculate_thermistor_coeffs,
        'set_motor_thermistor_coeffs': utils.set_motor_thermistor_coeffs,
    }

    # Import a bunch of variables and functions from various sources
    interactive_variables.update(_import_from(ShellVariables))
    interactive_variables.update(_import_from(enums))
    interactive_variables.update(_import_from(config))

    private_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'mdrive_private')
    if os.path.isfile(os.path.join(private_path, '__init__.py')):
        print("loading private plugins...")
        sys.path.insert(0, private_path)
        import mdrive_private
        mdrive_private.load_mtool_plugins(interactive_variables)

    async def mount(obj):
        serial_number_str = await utils.get_serial_number_str(obj)
        if not args.serial_number is None and serial_number_str != args.serial_number:
            return None
        if hasattr(obj, '_otp_valid_property') and (not await obj._otp_valid_property.read()):
            logger.warn('Device {}: Not a genuine MWDrive! Some features may not work as expected.'.format(serial_number_str))
            return ('device ' + serial_number_str, serial_number_str, 'dev')
        await utils.attach_metadata(obj)
        fw_version_str = '???' if obj._fw_version is None else 'v{}.{}.{}'.format(*obj._fw_version)
        return (f"{obj._board.display_name if not obj._board is None else 'device'} {serial_number_str} (firmware {fw_version_str})", serial_number_str, "mdrv")

    fibre.launch_shell(args, mount,
                       interactive_variables,
                       ShellVariables.devices,
                       print_banner, print_help,
                       logger)
