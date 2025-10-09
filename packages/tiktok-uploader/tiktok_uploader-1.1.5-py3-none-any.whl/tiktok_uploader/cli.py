"""
CLI is a controller for the command line use of this library
"""

import datetime
from argparse import ArgumentParser, Namespace
from os.path import exists, join

from tiktok_uploader.auth import login_accounts, save_cookies
from tiktok_uploader.types import ProxyDict
from tiktok_uploader.upload import upload_video


def main() -> None:
    """
    Passes arguments into the program
    """
    args = get_uploader_args()
    validate_uploader_args(args)

    # parse args
    schedule = parse_schedule(args.schedule)
    proxy = parse_proxy(args.proxy)
    product_id = args.product_id
    visibility = args.visibility

    # runs the program using the arguments provided
    result = upload_video(
        filename=args.video,
        description=args.description,
        schedule=schedule,
        username=args.username,
        password=args.password,
        cookies=args.cookies,
        proxy=proxy,
        product_id=product_id,
        cover=args.cover,
        visibility=visibility,
        sessionid=args.sessionid,
        headless=not args.attach,
    )

    print("-------------------------")
    if result:
        print("Error while uploading video")
    else:
        print("Video uploaded successfully")
    print("-------------------------")


def get_uploader_args() -> Namespace:
    """
    Generates a parser which is used to get all of the video's information
    """
    parser = ArgumentParser(
        description="TikTok uploader is a video uploader which can upload a"
        + "video from your computer to the TikTok using selenium automation"
    )

    # primary arguments
    parser.add_argument("-v", "--video", help="Video file", required=True)
    parser.add_argument("-d", "--description", help="Description", default="")

    # secondary arguments
    parser.add_argument(
        "-t",
        "--schedule",
        help="Schedule UTC time in %%Y-%%m-%%d %%H:%%M format ",
        default=None,
    )
    parser.add_argument(
        "--proxy", help="Proxy user:pass@host:port or host:port format", default=None
    )
    parser.add_argument(
        "--product-id",
        help="ID of the product to link in the video (if applicable)",
        default=None,
    )
    parser.add_argument(
        "--visibility",
        help="Video visibility: everyone (default), friends, or only_you",
        choices=["everyone", "friends", "only_you"],
        default="everyone",
    )
    parser.add_argument("--cover", help="Custom cover image file", default=None)

    # authentication arguments
    parser.add_argument("-c", "--cookies", help="The cookies you want to use")
    parser.add_argument("-s", "--sessionid", help="The session id you want to use")

    parser.add_argument("-u", "--username", help="Your TikTok email / username")
    parser.add_argument("-p", "--password", help="Your TikTok password")

    # selenium arguments
    parser.add_argument(
        "--attach",
        "-a",
        action="store_true",
        default=False,
        help="Runs the program in headless mode (no browser window)",
    )

    return parser.parse_args()


def validate_uploader_args(args: Namespace) -> None:
    """
    Preforms validation on each input given
    """

    # Makes sure the video file exists
    if not exists(args.video):
        raise FileNotFoundError(f"Could not find the video file at {args.video}")

    # Makes sure the optional cover image file exists
    if args.cover and not exists(args.cover):
        raise FileNotFoundError(f"Could not find the cover image file at {args.cover}")

    # User can not pass in both cookies and username / password
    if args.cookies and (args.username or args.password):
        raise ValueError("You can not pass in both cookies and username / password")


def auth() -> None:
    """
    Authenticates the user
    """
    args = get_auth_args()
    validate_auth_args(args=args)

    # runs the program using the arguments provided
    if args.input:
        login_info = get_login_info(path=args.input, header=args.header)
    else:
        login_info = [(args.username, args.password)]

    username_and_cookies = login_accounts(accounts=login_info)

    for username, cookies in username_and_cookies.items():
        save_cookies(path=join(args.output, username + ".txt"), cookies=cookies)


def get_auth_args() -> Namespace:
    """
    Generates a parser which is used to get all of the authentication information
    """
    parser = ArgumentParser(
        description="TikTok Auth is a program which can log you into multiple accounts sequentially"
    )

    # authentication arguments
    parser.add_argument(
        "-o", "--output", default="tmp", help="The output folder to save the cookies to"
    )
    parser.add_argument("-i", "--input", help="A csv file with username and password")
    # parser.add_argument('-h', '--header', default=True,
    # help='The header of the csv file which contains the username and password')
    parser.add_argument("-u", "--username", help="Your TikTok email / username")
    parser.add_argument("-p", "--password", help="Your TikTok password")

    return parser.parse_args()


def validate_auth_args(args: Namespace) -> None:
    """
    Preforms validation on each input given
    """
    # username and password or input files are mutually exclusive
    if args.username and args.password and args.input:
        raise ValueError("You can not pass in both username / password and input file")


def get_login_info(path: str, header: bool = True) -> list[tuple[str, str]]:
    """
    Parses the input file into a list of usernames and passwords
    """

    def extract_username_and_pass(input_str: str) -> tuple[str, str]:
        split_string = input_str.strip().split(",")
        if len(split_string) != 2:
            raise ValueError(f"{input_str} not valid")

        user, password = split_string

        return user, password

    with open(path, encoding="utf-8") as file:
        parsed_file = file.readlines()
        if header:
            parsed_file = parsed_file[1:]

        return [extract_username_and_pass(line) for line in parsed_file]


def parse_schedule(schedule_raw: str | None) -> datetime.datetime | None:
    return (
        datetime.datetime.strptime(schedule_raw, "%Y-%m-%d %H:%M")
        if schedule_raw
        else None
    )


def parse_proxy(proxy_raw: str | None) -> ProxyDict:
    proxy: ProxyDict = {}
    if proxy_raw:
        if "@" in proxy_raw:
            proxy["user"] = proxy_raw.split("@")[0].split(":")[0]
            proxy["password"] = proxy_raw.split("@")[0].split(":")[1]
            proxy["host"] = proxy_raw.split("@")[1].split(":")[0]
            proxy["port"] = proxy_raw.split("@")[1].split(":")[1]
        else:
            proxy["host"] = proxy_raw.split(":")[0]
            proxy["port"] = proxy_raw.split(":")[1]
    return proxy
