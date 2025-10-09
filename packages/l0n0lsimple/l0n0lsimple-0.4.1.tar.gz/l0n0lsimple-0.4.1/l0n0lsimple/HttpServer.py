from aiohttp import web
import argparse


def main():
    parser = argparse.ArgumentParser(description="启动一个 aiohttp 静态文件服务器。")
    parser.add_argument(
        'directory',
        type=str,
        help='要提供静态文件的目录路径。'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='服务器绑定的主机地址（默认：127.0.0.1）。'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8080,
        help='服务器绑定的端口号（默认：8080）。'
    )

    parser.add_argument("-s", "--show-index",
                        action="store_true", help="显示索引目录")

    args = parser.parse_args()

    app = web.Application()
    app.router.add_static('/', args.directory, show_index=args.show_index)
    web.run_app(app, host=args.host, port=args.port)


if __name__ == '__main__':
    main()