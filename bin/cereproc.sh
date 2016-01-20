voice="Hannah"
text="this is test text number 2"
output="temp.wav"
key="yveys9w8hipsc3di"

usage() { echo "./cereproc.sh [-v voicename] [-o output.wav] [-k key] -t \"text to say\""; exit 1; }

while getopts ":v:k:o:t:" o; do
    case "${o}" in
        v)
            voice=${OPTARG}
            ;;
        k)
            key=${OPTARG}
            ;;
        o)
            output=${OPTARG}
            ;;
        t)
            text=${OPTARG}
            ;;
        *)
            usage
            ;;
    esac
done
shift $((OPTIND-1))
xml=$(curl -Ss 'https://www.cereproc.com/livedemo.php' -H 'Pragma: no-cache' -H 'Origin: https://www.cereproc.com' -H 'Accept-Encoding: gzip, deflate' -H 'Accept-Language: en-US,en;q=1.8' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36' -H 'Content-Type: text/plain;charset=UTF-8' -H 'Accept: */*' -H 'Cache-Control: no-cache' -H 'Referer: https://www.cereproc.com/en/support/live_demo' -H "Cookie: Drupal.visitor.liveDemo=${key}; _gat=1; cookie-agreed=2; has_js=1; _ga=GA1.2.708457990.1453250578" -H 'Connection: keep-alive' -H 'DNT: 1' --data-binary "<speakExtended key=\"${key}\"><voice>${voice}</voice><text>${text}</text><audioFormat>wav</audioFormat>\\n</speakExtended>" --compressed)
url=$(echo $xml | sed 's#.*<url>\([a-zA-Z0-9\/\.\:]*\).*#\1#')
cmd=$(curl -Ss "$url" -o "${output}" -H 'Pragma: no-cache' -H 'DNT: 1' -H 'Accept-Encoding: identity;q=1, *;q=0' -H 'Accept-Language: en-US,en;q=0.8' -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36' -H 'Accept: */*' -H 'Cache-Control: no-cache' -H 'Referer: https://www.cereproc.com/en/support/live_demo' -H 'Connection: keep-alive' -H 'Range: bytes=0-' --compressed)

