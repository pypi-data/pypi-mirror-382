import curses
import subprocess
import time
import os
import shutil

PAGE_SIZE = 20          # 每页显示多少行
REFRESH_INTERVAL = 5    # 每 5 秒刷新一次服务状态


def get_services():
    """获取 systemctl 服务列表和状态"""
    result = subprocess.run(
        ["systemctl", "list-units", "--type=service", "--no-pager", "--all"],
        capture_output=True, text=True
    )
    services = []
    for line in result.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 4:
            name, load, active, sub = parts[:4]
            services.append((name, active))
    return services


def run_systemctl(service, action):
    result = subprocess.run(
        ["systemctl", action, service],
        capture_output=True, text=True
    )
    return result.stdout + result.stderr


def show_output(stdscr, title, output):
    stdscr.timeout(-1)
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(0, 0, title)
    for i, line in enumerate(str(output).splitlines()[:h-3]):
        stdscr.addstr(i+2, 0, line[:w-1])
    stdscr.addstr(h-1, 0, "按任意键返回")
    stdscr.refresh()
    stdscr.getch()
    stdscr.timeout(100)


def draw_ui(stdscr, services, page, current_row, sort_mode, search_query):
    h, w = stdscr.getmaxyx()
    total_pages = max(1, (len(services) + PAGE_SIZE - 1) // PAGE_SIZE)
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(services))
    page_services = services[start:end]

    # 修正 current_row 防止越界
    if current_row >= len(page_services):
        current_row = max(0, len(page_services) - 1)

    # 统计栏
    active_count = sum(1 for _, s in services if s == "active")
    inactive_count = sum(1 for _, s in services if s == "inactive")
    failed_count = sum(1 for _, s in services if s == "failed")

    stdscr.clear()
    stdscr.addstr(
        0, 0, f"Systemctl 管理器 (第 {page+1}/{total_pages} 页) ↑↓选择 ←→/PgUp/PgDn翻页 s启动 t停止 r重启 e启用 d禁用 u更新 q退出")
    stdscr.addstr(
        1, 0, f"[排序: {sort_mode}] [搜索: {search_query or '无'}] (n=按名字, a=按状态, /=搜索, 自动刷新 {REFRESH_INTERVAL}s)")
    stdscr.addstr(
        2, 0, f"[统计] active: {active_count} | inactive: {inactive_count} | failed: {failed_count}")

    for idx, (svc, state) in enumerate(page_services):
        color = curses.color_pair(0)
        if state == "active":
            color = curses.color_pair(1)
        elif state == "inactive":
            color = curses.color_pair(2)
        elif state == "failed":
            color = curses.color_pair(3)

        line = f"{svc:<40} {state}"
        line = line[:w-3]

        if idx == current_row:
            marker = "▶"
            stdscr.attron(curses.color_pair(4))
            stdscr.addstr(idx+4, 0, f"{marker} {line}", color)
            stdscr.attroff(curses.color_pair(4))
        else:
            stdscr.addstr(idx+4, 0, f"  {line}", color)

    stdscr.refresh()
    return page_services, total_pages, current_row


def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)   # active
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # inactive
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # failed
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_CYAN)    # highlight

    current_row = 0
    page = 0
    sort_mode = "name"
    search_query = ""
    last_refresh = 0

    stdscr.timeout(100)  # 每 100ms 检查一次输入

    last_key = None
    repeat_count = 0

    services = get_services()

    while True:
        now = time.time()
        if now - last_refresh > REFRESH_INTERVAL:
            services = get_services()
            last_refresh = now

        # 搜索过滤
        filtered = services
        if search_query:
            filtered = [s for s in services if search_query.lower()
                        in s[0].lower()]

        # 排序
        if sort_mode == "name":
            filtered.sort(key=lambda x: x[0])
        elif sort_mode == "state":
            order = {"active": 0, "inactive": 1, "failed": 2}
            filtered.sort(key=lambda x: order.get(x[1], 99))

        page_services, total_pages, current_row = draw_ui(
            stdscr, filtered, page, current_row, sort_mode, search_query)

        key = stdscr.getch()
        if key == -1:
            continue

        # 连续滚动检测
        if key == last_key:
            repeat_count += 1
        else:
            repeat_count = 0
        last_key = key

        step = 1
        if repeat_count > 5:
            step = 2
        if repeat_count > 10:
            step = 3

        if key == curses.KEY_UP:
            if current_row > 0:
                current_row -= step
            else:
                if page > 0:
                    page -= 1
                    current_row = PAGE_SIZE - 1
        elif key == curses.KEY_DOWN:
            if current_row < len(page_services) - 1:
                current_row += step
            else:
                if page < total_pages - 1:
                    page += 1
                    current_row = 0
        elif key in [curses.KEY_LEFT, curses.KEY_PPAGE] and page > 0:
            page -= 1
            current_row = 0
        elif key in [curses.KEY_RIGHT, curses.KEY_NPAGE] and page < total_pages - 1:
            page += 1
            current_row = 0
        elif key == ord("q"):
            break
        elif key in [ord("s"), ord("t"), ord("r")]:
            if page_services:
                svc = page_services[current_row][0]
                action = {"s": "start", "t": "stop", "r": "restart"}[chr(key)]
                output = run_systemctl(svc, action)
                show_output(stdscr, f"执行: systemctl {action} {svc}", output)
        elif key == ord("e"):  # enable
            if page_services:
                svc = page_services[current_row][0]
                output = run_systemctl(svc, "enable")
                show_output(stdscr, f"执行: systemctl enable {svc}", output)
        elif key == ord("d"):  # disable
            if page_services:
                svc = page_services[current_row][0]
                output = run_systemctl(svc, "disable")
                show_output(stdscr, f"执行: systemctl disable {svc}", output)
        elif key == ord("u"):  # update
            curses.echo()
            stdscr.timeout(-1)
            h, w = stdscr.getmaxyx()
            提示内容 = "请输入 .service 文件路径: "
            stdscr.addstr(h-1, 0, 提示内容)
            filepath = stdscr.getstr(h-1, 25).decode("utf-8").strip()
            curses.noecho()
            stdscr.timeout(100)
            if filepath:
                svc_name = os.path.basename(filepath)
                target_path = f"/etc/systemd/system/{svc_name}"
                try:
                    shutil.copy(filepath, target_path)
                    subprocess.run(["systemctl", "daemon-reload"])
                    subprocess.run(["systemctl", "enable", "--now", svc_name])
                    msg = f"服务 {svc_name} 已更新并启动"
                except Exception as e:
                    msg = f"更新失败: {e}"
                show_output(stdscr, "更新结果", msg)
        elif key == ord("n"):
            sort_mode = "name"
            page = 0
            current_row = 0
        elif key == ord("a"):
            sort_mode = "state"
            page = 0
            current_row = 0
        elif key == ord("/"):
            curses.echo()
            stdscr.timeout(-1)
            stdscr.addstr(curses.LINES-1, 0, "搜索: ")
            search_query = stdscr.getstr(curses.LINES-1, 6).decode("utf-8")
            curses.noecho()
            stdscr.timeout(100)
            page = 0
            current_row = 0


def run():
    curses.wrapper(main)


if __name__ == "__main__":
    run()
