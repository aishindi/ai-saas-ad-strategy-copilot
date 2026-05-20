import time, base64, requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/ask"

# Logo embedded as base64 so no file path needed
LOGO_B64 = "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"

st.set_page_config(
    page_title="AdCopilot — AI SaaS Ad Strategy",
    page_icon="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAYAAABccqhmAAAaLElEQVR4nO2dW7IsR3WGszr2JM4oDDK8+8kBRuhmhMEmwhcZyUJCImzCL56EA2yEbMByBEKA0AER9ijQuRgGoWGUH3ZXdV7WtSors6r7XxFSnNP7qz9L1Zlfr+6dqh5eeu1RGAJRI/VgKNmRhmlOyWMYniv/kLBC3swpDM3RB1nzwkhcHxPHhFvyzodauZQlxiU5nlnGjSJHZrrmLceNRq7ExbFVbjRyOmPl7g64+MWrhMVPMyFg8ds48+K/J5Tpv+fFH0IIJ5Jhnq2CHWiY5pQ8fnaO4z16/88gHzDKP045w0osOWFcy8oebJ4oOSbcknc+1MqlLDEuyfHMMm4QOTLTNW85bjByLDPG/9jn42DkdMbDnWY4r74SiC+iwEEC5jxIwMGtlkCCzi9gO5TAKYHzai+B8dILKeNCAv48SMDBVZXApcEX5vcEmPMqSOAU/6WTBKZWSZxrZB4k4M+DBBzcJhKY3vAnHW7KtZPAyfTkbCOB4gJYLyYkIIRDAiLj5zaTQPxQcUqtJHCiBmkgAfb9ECTg4SCBvA4qAfKUWkjg8hagjQRS20ECyeGQgIW7eglkXfG2Ekg+A9hQAvN/2KInBxJQOEggrwNLYPrRePnLdhI4FT+tLwGitVmQBwkoHCSQ18ElkPx4KwmUAiACVkhgFN4O+PMgAYWDBPKCBGSO3glIBDglQLzXhwQ8eZCAlbsZCZzfQteVAL8TkAgwSkB4rw8JePIgASt3ExKYkZoSkHcCEgGKBJIfQwLKuJAAySzjIAEWFhh9JyARwEiAfBgSUMaFBEhmGQcJsDDD2HYCEgEj9VfXxYQEPHmQgJWDBFiYYE4hDGsvumm+QQLKuJAAySzjIAEWzpjTfOSyiz6SHCQgcJAAJKBnFexGEog+A3BLYBQ5SEDgIAFIQM8q2A0kkG0EMkug+J95IAEvBwlAAnpWwVaWALETUJUAe20hAS8HCUACelbBVpQAsxPQ/XZA5iABgYMEIAE9q2BVziYBYScgKQEWzTiVYVlIwJ0HCVi5m5BA9NmcLgFlJ2AigZHnykEgAS8HCUACelbBrpSAYSfgEEK2yw8S4PNmDhIguZSFBMS8BhIw7gQk3w7QBQlcOEiA5FIWEhDz1kkg4mgJWO4JOM5HQgIpCwkUh0ICFq6ZBLLOvZSA756AkEDJQgLFoZCAhdtHJ6DdE5C4npBAwUICxaGQgIVrIoHilGIJSPcEHMmjJwgSSFlIoDgUErBwfSWw/J6AkEDJQgLFoZCAhev3doC7J6Btrz8kULKQQHEoJGDhNpcAeSnW3xMQEihZSKA4FBKwcO07gTr3BIQEShYSKA6FBCxcWwmciItZXitIABIQxoUEZMbPbSaB4jSKjUDoBGiG5yABcx4k4ODadAL5RqCxCBYGgQTkAyABmgkBErBxm0gg+YCf3QgECdAMz0EC5jxIwMFt2wmIXw4KCdAMz0EC5jxIwMFtJ4ET9TgkoDM8BwmY8yABB1dVAvPdvOmdgFkAJEAzPAcJmPMgAQdXvxPgvx04C4AEaIbnIAFzHiTg4OpKQN4JmAVAAjTDc5CAOQ8ScHD1JDC9BaC/4YcIgARohucgAXMeJODgVktgDIHeCUgXJKAyPAcJmPMgAQe3vhOw7wS0cpAAJCCMCwnIjJ9bJ4HT/Agk4M+DBBQOEshrbxI4JY9AAv48SEDhIIG89iSB0+VxSIDnlDxIQOEggbx2IoGx/Hbg7GBIwJgHCSgcJJDXHiRAfztwdjAkYMyDBBQOEsirtwSYrcCQAM8peZCAwkECefWUgLAVGBLgOSUPElA4SCCvXhJQtgJDAjyn5EECCgcJ5NVDAif9YkICPKfkQQIKBwnk1VoCyU5ASCDmIAFPHiRg5fYlgeLLQSGBmIMEPHmQgJXbjwTIewJCAjEHCXjyIAErtw8JsPcEhARiDhLw5EECVq6/BMQvB4UEYg4S8ORBAlaurwTuaOT88/EepnPOwHAZmWeDjYsYnhtCGEYDZ8zLGJYdQghjCdOckscwPEcfMLNC3swpDM0J4w4h/PS9zxc/+8Zf/+7ylyGEcTT4ouCYk7XkqfO2HOLCEuNWm7cSl/2AOI1F80zlBuGmoNPB9PEpgE7An3fwToBa/CGE8NP/zh5HJ2Dk+nQC8k1Bo4MhgZi7bQm8zyz+qSCBpVx7CZzqXExIgOeUvINJQFv8U0ECS7m2Epg3AkECNMOyNyyBxQUJGLl2Ekg2AkECNMOyNymBlQUJGLk2Eig2AkECNMOykABbxduAqSABI7e9BMiNQJAAzbAsJMAWJJD+dW8SGJ596wl9TqPh+R7F8S5ANIKYaeGys2Wnv4kz5jHPWsGONExzSp4wS2mOVaKaN3MC87P/+pwcoFSyPyAuyzwjOeZkq8zbcoiBelDkeGYZN4ocmWmYZ+KXg6IToBmWvdJOYO3iDwGdwF47Ab4DiGh0AjTDslfSCdRY+HmhE0j/2rsT0AVwDoAEaIZlDy6Bn/2EX/x/+befXPLGEN5/zycKSCD9a08J6DsBz2l4O0AzLHvgtwOWxT/leRd/CHg7sKe3A8OX3n4yLjcvzQjjXQB0Av68jTuBD4wLfyp8MCiMe5BOwL4T0MqhEyC4/XcC3sVfo9AJpH/t0QncdwARjU7AmXfwTuCDH6uv4p8yjz/QDrQWOoH0ry07gbv7H13+q5f9/9s0M601mjsD0fA8G2xcxPDcEHA/gfuSFv/X/+6T8MFPPrd28RfH/9Xf/O7BdEbqy+3i+chcoCrzthziwhLjVpu3Epf9gDgNbp4NX3r7aflSjE7An3egTuDnyqu+YfFzPzOVSwJnBp2AhfN3ApEAsiMgAX/eASTw8x//Mct//ZVPQhiDtPirFSSgZy3jfBKgvx34/EfL82LiBvZcUiAaXsy0cNmVo7nByBnzmGerYAcapjklT5idOSct/q+9cv9BX4vFH0II77/3+U9DiN6haLV4PjLhVeZtOcRIPShyPLOMG0QuzyTuCYjPBFbl7fAzgV/8SF/4E9ujxhBM9yzEZwJWzv6ZgPztwOc/ohNw5u2oE7Au/t6FToBnlnG2TuBOfUU+/xGdgDOvcycgLfwQQvjaK4/40E6FToDPWsbpncCd/B8PCRxRAr/4T+FV/+8fZVmQgDnvCiVwNz0ICUTQQSXwS2HhhxDCX5wXf9kx9JIAPS4kwGct43gJ3MUPQgIRdDAJSIt/WvhkHiTgz7siCTjuCTgYOWteGquOGw0vZlq47MrR3GDkjHnMTCnYgYZp7r48i5/MG4o/NC563JH/UXH4svnIhFeZt+UQI/WgyPHMMm4ouPLXgOgEUmjHnYC48L+Zv9dXxu3RACRjohPo0QnQ3w0ICaRQJwl8+G65wF9+9VEYQgi//A9+8X/1m9x7fWXcxg1AubghgdYSEL8cFBKIoMYS+PDdZ6j08KGw8EO4LP5ibKsEGhck0FcCvADODCQQQY0k8Ctm8Uv11Vcf6Z0FJKBwtycB+duBzwfz13swcta8NFYdNxpezLRw2ZWjucHIGfOIZ2vx4mfyirGF2Wl6/jaqMYTs3OgTLTmmFs9HJrzKvC2HGKkHRY5nlnB30qtCfDA6gQhq0AlY6uVXs/f6Qp61E+hZ6ATadwKnOkZFJ1C7E/BUkbmyE+hZ6ATadgKnGYYESIbnIIGtChJoJ4H5MwBIgGd4DhLYqiCBNhJIfgtQ571VFLD4PRgfe62fCfzqh74P/15+7XEZSI3NPJ/4TMDDMeFV5m05RMvPBIrfAqAT4BmeW9cJLFv8U1b5ZB2mEzCMiU5g206A3AeAToBneM7fCXzkXPghhPCV1x4Tr/AVO4GGZZ1n6AS26wTYjUCQAM/wnF0C0uL/yj88TgOyohd3JQk0LkiA50LYXgLiRiC8HeAZntPfDnz0jnHxE2OyY9d8O9C4rPMMbwfqvx2QtwIHdAISw3N0J/BQWPh/Hi38Is/6yl2hE+hV6AR4LoTtOoHTMvPyJ4xOIIIiTlz8r6ev+mReo06gZ6ET4LmUrdcJ3C03Lz8IOoEL9PCdz0pnHkIIn0pvCTz18muPH1zObXkn0LPQCfBcCPU7AddOQHQCPENxD3/AL/7zq37VL+H48N1nLnnoBNx5t9gJuHcCQgI8M3EPf/BZcfG/9Prj8NE7z2zyDTyQACTgmbenmIYEeFzkIubX0sL/1uPw0uuPw8ONFv9Uh5GAMiYkwHMpu1wCp5yGBHhc5AZt8T8J958JbLv4p4IEIAHLvI1+DXj5dAAfDMqnmXO//ndt4e+ghmD7YLBhzWMrcwgfDPJcCOs+GGS/HRidAI/HnLT4X/zWE9t/y0ZFv8IbOoGGlaxVjUMnQHIp6+sExG8HRifA478RFn4I94t/ql28yk6FTsCdd82dALMTEBKQLry0+F9840kSOdUuFthUggR6FSRAZ20tAeGegJBAzv7m35RX/WnxZ5FT7WKBTcVIoGdBAnTWlhJQdgJCAhMrLf4XzgufzNzRGoME+OBblYBhJ+DlBzJ3KSsXBul6D0bOmpfGquNGw4uL/83Lqz6b2av3J6o4x3m19Sh63FH+ccotmo/CuKvnrcQx4VXmbTnESD2YPTR/BoBOoAQ+Ni5802cHPV5omTH31QkIr8j8j1MOnQDJhaB3Ao57Al6fBH77vc8UDz//7achhBA+/r5x8ROnKUqgdbkl0LDmc4MEzHmVJVD8FuBWJEAt/hBC+Pj79ONTPf/mE/ndkiaBHuWRQOuCBPx5FSWw4J6Ax5cAt/ilev7bT2yL++gS6FGQgD+vkgTYW4LNzwebauGseWk0f70HI8fnLVv8T4vhxbGtXOtirn+vc0zGHYo/0Kwyh5bPR2Hc1fNW4phwS975UCuXsvcPircEu/ZOQKt54cfjWl/hd9AJkOPurBNIxkUn4M9b2QmotwS71k5gWQ3F8HvvBFh3W9kGhU5ACN+4EzhJYyfwlUhgfV23BHoVJCCEbyiBU52LeSAJOEodd4EEehUk4OVuQwKXnYDC2FNdgwS+/PZTw4AhPPfWPXdoCWRjQgJe7volkN4TUBg74a5cAtPi1y8mJLBFQQJCeGUJJL8GhASixZ/FVpNAj9qrBIQxIQEhvKIE6J2AU8DiX7VcfmD9FUqdX7VEASJ3X7MEVv+qZbiEFL9q2Ull15Y8v14SYJ7z5Bxnjj6gzryVOGHc1fNW4phwS546b5mNQLfUCZi5W+kEehQ6AYXbrhOQdwIKYyccJJACkICp6MVt5SABc54wb/VvBxbGTjhIIAV2IAF2XEjgwt24BIRbgl0OOPJnAv/zr39U7T78z731NPruvWN8JsCOa/lMoFHR7/WtHD4TMOcR89a+E9DK7agTqLn4Qwjht9/7TPZlG+gEahU6AQ9XrxM45T/g6mgSqL34p1orgV5llUDPggQ8XB0JnKwXfTrAzHWUwFaLf6rDSMD6Cg8JXLgbk0C6FVjInGrvEvjfjRf/VMeQwLBvCTBjQgIebp0E5m8HviYJdCmrBJoXJFCwkMBcybcDQwIr6xok0KMggeTwlhKI9gFAAlVKlUCvggQKFhKgvx0YElhZkICpirEhgeTwFhIgdgJCAlVqBxKgx4YECvaGJcDcExASsJTn9629ChKQD7h1CQg7ASEBtSxPDiRgKkhAqA0loOwEhATUujIJ9CxIQKiNJGDYCXgwCfQohwSalukVvqcEyoEhAaE2kIBxJ+BxJNCtIAF/DfO/koIEhKosgfKmoCwLCahlfXJaFyQACTDj0jcFZU8EElDr6BLoUZCAO6+WBIp9AJBAhTq0BDoVJODOqyEB+aag7IlAAmpBAmrRixsS8OStlQD75aCQQIXqLAF2bEgAEjg/IN4SDBKQa9lFb1uQgHHcG5WAekswSECoxeZtW5CAcdwblMAp/wF7AiIDCVTjalZ0PawS6FmQgDLuBhI41buYO5FAj3Jc9OYFCagMz12/BMqdgMIgR5BA2xqSP+7yU/8Q9isByzybOUjAk2edj/ROQGEQSEAYFxLwFyQgcNtLgN8JKAwCCQjjHl0CPQoSELhtJSDvBBQG2a8EehUksKogAYHbTgL6TkBhEEggL0hgVUECAreNBGw7AYVBIIG89iMBcewdSIAcFxIQuPoSsO8EtHI3JAF+4UAC1oIEvFxdCfh2Alq5W5GAuLghAWtBAl6ungT8OwGtHCQQukvAurh38DYKEvBydSSwbCegleshgR7lkEDz2rMEsjEhAS+3XgLLdwJaucYS6FZWCTStoRgeEjDm3YgE6G8HFg6GBIS6Bgn0KEjgwjWWAP/twMLBkIBQkMCyggQuXEMJyN8OLBwMCQjV4wM/tSABnlPyrlgC+rcDCwdDAkJBAssKErhwDSRA7ASEBKoVJCAWOy4kcOE2lgCzExASMJVlzI4SUD+LgAT8eVcmAWEnICSglef3rbtbYJCAwCl5VyQBZSfgASXQuHYtgfN5eSTQqyABPm/mNpBA+b8DQwLu8kigee1ZApbFbeUgAYHjxy23ApP8cSTQq8wS6FG7lcAACeRsYwnQW4FJHhLQ6iok0LwggYJtKAH+pqAkDwloBQksKUigYBtJQL4pKDkIJKDVsSXQqyCBgm0ggWIjECRQpyCBJQUJFOzGEiA3AkECdQoSkIseGxIo2A0lwG4EggQMteiityt1cUMCBHdbEhA3AkECci03b6MaIAGOYdkbk4C6EehwEmhckECdggTkA7aSAPnFIJCAr1wXvUc5JNC0TIsbEijYihKgdwISAZAAP+489l4/8AsBEhAYlr0BCfA7AYmAI0igfV2ZBHoUJNBNAvJOQCIAEpDHhQQWFiTQRQL6TkAiYM8S+NN//sMD+si69cV/+n02jk0Cf/aP/9fk/L789lN+HEECz70lHFexXnzjSTkOJNBcAradgETALUvgi9/NF395Mj0l8Ky0+KfqKIEX3njyYNU8gwRKdqEE7DsBrdyVS+AL3/39A7mt6iuBZ7/z9IG5ze8ggRfevLzyQwI0w3P1JeDbCWjlrlQCX4he+fcogWe/E+XtUALz4o+uByRAMzxXVwLDn/zLH8aSMJyfhSuuyEizzLO2iCMZYlxldcyshWOZ0chZ89Jo/rkejZw1L41Vx42GFzMtnGk+jhvPW4YdabjevJU4Volq3syNS3cCWrmddALkuBZTWrmVnYA9L43mn+PByFnz0lh1XMsrvJVDJ7BpJ7B8J6CVgwSMnDUvjYYEIggSSFnDvF23E9DKQQJGzpqXRkMCEQQJpKwyh04hDCsvupGDBIycNS+NhgQiCBJIWSFv/nZgSIDOKjIhgSIWEoi5Y0kg+XZgSIDOKjIhgSIWEoi540gg2wkICUACnrw0FhKIuWNIgNgJCAlAAp68NBYSiLn9S4DZCQgJQAKevDQWEoi5fUtAuCcgJAAJePLSWEgg5vYrAWUnICQACXjy0lhIIOb2KQHDTkBIABLw5KWxkEDM7U8Cxp2AkAAk4MlLYyGBmNuXBE4hhAES4E8EElial8ZCAjG3GwkMznsCQgKQgCcvjYUEYm4fEjj5LyYkAAl48tJYSCDm+kug2AgECfAnAgkszUtjIYGY6ysBciMQJMCfCCSwNC+NhQRirp8ETslDkIDCQALr8tJYSCDmmktgCEHZCAQJ8CcCCSzNS2MhgZhr3wmoG4EgAf5EIIGleWksJBBzbSVACyALgAT4E4EElualsZBAzLWTQCyAEocEFAYSWJeXxkICMbepBIaJ47cCEwGQAH8ikMDSvDQWEoi57TsB+evBiQBIgD8RSGBpXhoLCcTcthI4ZRednxqQgMJAAuvy0lhIIOaqSiAhk52A6AQcHCSQBkAC/rwddALFTsBRmxaQgMJAAuvy0lhIIOZWS6DoAchbgqETcHCQQBoACfjzOnYC7E5ASMDBQQJpACTgz+skAW4n4ECGCoNAAvyJQAJL89JYSCDm3BIYKE7dCQgJODhIIA2ABPx5jTsBXgBzHwAJuDhIIA2ABPx59SVAJo4hhNMoP9uQwBIOEkgDIAF/Xj0JDFLeeSeg8mxDAn4OEkgDIAF/XoO3A9FOQGX2QAJ+DhJIAyABf946CZR3/M6QbCcgOgGaYzIhgSQaEoig/UhAnLfETkBhxiacUpCAwkAC6/LSWEgg5koTcPOW2QkICdAckwkJJNGQQAT1kUA5MM1JOwEhAZpjMiGBJBoSiKC2Ehgu/9YlIN4TEJ8JcByTCQkk0ZBABPV9O8Byhp2AzCopOKUgAYWBBNblpbE3KgHmU39eAtJOQEhA5ZhMSCCJhgQiaLt5O//NIwHzPQEhAY5jMiGBJBoSiKD687Z4FqwSOPkuJiRAc0wmJJBEQwIRVG/eMjv9bRKYNwJBAjQDCchZHg4SyKD183bgGDYzk0CyEQgSoBlIQM7ycJBABi2ft+XVXiCBYiMQJEAzkICc5eEggQzyz9uB5ZwSIDcCQQI0AwnIWR4OEsgg+7wdVM4xH9mNQJAAzUACcpaHgwQySOcGc55xPoobgVZKYCg5W57IQgKQwOK8NPZAEkjXkzXPMM/UjUArJJCeAiTg5yCBNOA2JVDu7vPkKfNMFsA5ABKgGUhAzvJwkEAGZc3+VhLQdwKeAypIYEg5W57IQgKQwOK8NHZnEhhCGIoNPltIwLYT8BywUgITgRuNLuEggTTgOiUwhPw/cmMJ2HcCWjldAvcUJODnIIGQr48rkgDzXn9bCfh2Alo5uwSGe86WJ7KQACSwOC+NbSyB5FW/tQT8OwGtnE0C8wUYtWkBCSgMJLAuL43dWAJD9I9xPm4jgWU7Aa2cXQJnLn8PRHNnVmUgAT6ryIQEitgNJMC/0HWSwPKdgFbOL4Hpb7QMIAGFgQTW5aWxFSRwP4+jz/TXzce6Eli3E9DKLZNA/CjbMkEC/IlAAkvz0linBMr5SpzmXiSwfieglVsngZyYjDqEYN0pBQlAAp68NJZ/dR/y+Vjjg8GktpTA/wNs/B/Dkt2dngAAAABJRU5ErkJggg==",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Inline CSS + top-bar HTML ──────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Instrument+Serif:ital@0;1&display=swap');

/* Reset */
*, *::before, *::after {{ box-sizing: border-box; }}

/* Hide ALL Streamlit chrome — header, toolbar, deploy menu, fullscreen, collapse */
header[data-testid="stHeader"],
#MainMenu,
footer,
.stDeployButton,
button[title="View fullscreen"],
[data-testid="collapsedControl"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stAppDeployButton,
iframe[title="streamlit_analytics"],
div[data-testid="stToolbarActions"],
div[class*="StatusWidget"],
div[class*="toolbar"] {{ display: none !important; }}

/* Kill the white bar Streamlit renders above the app content */
.stApp > div:first-child > div:first-child:not([data-testid="stSidebar"]):not(.block-container) {{
    display: none !important;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-font-smoothing: antialiased;
}}

/* ── App shell ── */
.stApp {{
    background: #f7f8fa;
    background-image:
        radial-gradient(ellipse 70% 50% at 15% 0%,  rgba(99,155,237,0.13) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 85% 90%, rgba(140,105,230,0.10) 0%, transparent 55%);
    min-height: 100vh;
}}

/* Top-bar clearance */
.stApp > div {{ padding-top: 28px; }}

.block-container {{
    padding-top: 1.25rem !important;
    padding-bottom: 100px !important;
    max-width: 800px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}}

/* ── Fixed top bar — full viewport width ── */
#ac-topbar {{
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 58px;
    background: rgba(255,255,255,0.88);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid rgba(0,0,0,0.07);
    display: flex;
    align-items: center;
    padding: 0 24px;
    gap: 12px;
    z-index: 9999;
}}

#ac-topbar img.ac-logo {{
    width: 32px;
    height: 32px;
    border-radius: 8px;
    flex-shrink: 0;
    display: block;
}}

#ac-topbar .ac-name {{
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: 1.12rem;
    color: #111827;
    font-style: italic;
    letter-spacing: -0.01em;
    white-space: nowrap;
    line-height: 1;
}}

#ac-topbar .ac-sep {{
    width: 1px;
    height: 18px;
    background: #e2e5ea;
    flex-shrink: 0;
}}

#ac-topbar .ac-sub {{
    font-size: 0.76rem;
    color: #9ca3af;
    font-weight: 400;
    letter-spacing: 0.01em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

#ac-topbar .ac-pill {{
    margin-left: auto;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 0.70rem;
    font-weight: 600;
    color: #6b7280;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    white-space: nowrap;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: #ffffff !important;
    border-right: 1px solid #eaecf0 !important;
    box-shadow: none !important;
    top: 58px !important;
    height: calc(100vh - 58px) !important;
    position: fixed !important;
}}

/* Kill Streamlit's own inner wrapper top spacing — this is the pink gap source */
section[data-testid="stSidebar"] > div:first-child {{
    padding-top: 0 !important;
    margin-top: 0 !important;
    padding-bottom: 1.4rem !important;
    overflow-y: auto !important;
    height: 100% !important;
}}

/* The actual scrollable content block inside sidebar */
section[data-testid="stSidebar"] > div > div:first-child {{
    padding-top: 1.1rem !important;
    margin-top: 0 !important;
}}

/* Hide only the collapse/expand toggle buttons — sidebar stays permanently visible */
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] {{ display: none !important; }}

/* Sidebar section labels */
.sb-label {{
    font-size: 0.67rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-top: 1.1rem;
    margin-bottom: 0.45rem;
}}

/* Hide native Streamlit widget labels — we render our own .sb-label above each */
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stTextInput label {{ display: none !important; }}

section[data-testid="stSidebar"] .stSelectbox > div > div {{
    background: #f9fafb !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 0.86rem !important;
    color: #111827 !important;
    min-height: 38px !important;
    box-shadow: none !important;
}}

section[data-testid="stSidebar"] .stSelectbox > div > div:focus-within {{
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.10) !important;
}}

section[data-testid="stSidebar"] .stTextInput > div > div {{
    background: #f9fafb !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
    font-size: 0.86rem !important;
    min-height: 38px !important;
    box-shadow: none !important;
}}

section[data-testid="stSidebar"] .stTextInput > div > div input {{
    color: #111827 !important;
    padding: 0 10px !important;
}}

section[data-testid="stSidebar"] .stCheckbox label {{
    display: flex !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
}}

/* New Analysis button */
section[data-testid="stSidebar"] .stButton > button {{
    background: #111827 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.84rem !important;
    font-weight: 600 !important;
    height: 38px !important;
    letter-spacing: 0.01em;
    box-shadow: none !important;
    transition: background 0.15s ease;
    width: 100% !important;
    margin-top: 0 !important;
}}

section[data-testid="stSidebar"] .stButton > button:hover {{
    background: #1f2937 !important;
}}

section[data-testid="stSidebar"] hr {{
    border: none !important;
    border-top: 1px solid #f0f1f3 !important;
    margin: 1rem 0 !important;
}}

/* Run meta card */
.run-card {{
    background: #f9fafb;
    border: 1px solid #eaecf0;
    border-radius: 8px;
    padding: 10px 12px;
}}

.run-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 2.5px 0;
}}

.run-lbl {{ font-size: 0.73rem; color: #9ca3af; font-weight: 500; }}
.run-val {{ font-size: 0.73rem; color: #111827; font-weight: 600; }}
.hit  {{ color: #16a34a !important; }}
.miss {{ color: #dc2626 !important; }}

/* ── Suggestion cards ── */
.card-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin: 0.5rem 0 2rem;
}}

.s-card {{
    background: #ffffff;
    border: 1px solid #eaecf0;
    border-radius: 12px;
    padding: 14px 16px;
    cursor: default;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    position: relative;
    overflow: hidden;
}}

.s-card::after {{
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(99,102,241,0.04), rgba(139,92,246,0.03));
    opacity: 0;
    transition: opacity .18s;
}}

.s-card:hover::after {{ opacity: 1; }}

.s-card-label {{
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #6366f1;
    margin-bottom: 6px;
    display: block;
}}

.s-card-text {{
    font-size: 0.84rem;
    color: #374151;
    line-height: 1.5;
}}

/* ── Chat messages ── */
div[data-testid="stChatMessage"] {{
    background: #ffffff !important;
    border: 1px solid #eaecf0 !important;
    border-radius: 14px !important;
    padding: 0.55rem 0.8rem !important;
    margin-bottom: 0.6rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
}}

div[data-testid="stChatMessage"] p,
div[data-testid="stChatMessage"] li {{
    color: #1f2937 !important;
    font-size: 0.92rem !important;
    line-height: 1.68 !important;
}}

div[data-testid="stChatMessage"] strong {{ color: #111827 !important; font-weight: 600 !important; }}
div[data-testid="stChatMessage"] h1,
div[data-testid="stChatMessage"] h2,
div[data-testid="stChatMessage"] h3 {{ color: #111827 !important; font-size: 1rem !important; }}
div[data-testid="stChatMessage"] code {{
    background: #f3f4f6 !important;
    color: #6366f1 !important;
    border-radius: 4px; padding: 1px 5px; font-size: 0.85em;
}}

/* ── Chat input — fully uniform white, no grey anywhere ── */
/* Kill every wrapper layer Streamlit nests */
div[data-testid="stBottom"],
div[data-testid="stBottom"] > div,
div[data-testid="stBottom"] > div > div,
div[data-testid="stBottom"] > div > div > div {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}}

div[data-testid="stBottom"] {{
    position: fixed !important;
    bottom: 0 !important;
    left: 305px !important;
    right: 0 !important;
    width: auto !important;
    padding: 12px 32px 20px !important;
    background: linear-gradient(
        180deg,
        rgba(247,248,250,0) 0%,
        rgba(247,248,250,0.97) 28%,
        #f7f8fa 100%
    ) !important;
    z-index: 900 !important;
}}

/* The actual input pill — pure white, uniform */
div[data-testid="stChatInput"] {{
    background: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05), 0 4px 16px rgba(0,0,0,0.05) !important;
    overflow: hidden !important;
}}

/* Every child div of the input must also be white */
div[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] > div > div,
div[data-testid="stChatInput"] > div > div > div {{
    background: #ffffff !important;
    border: none !important;
    box-shadow: none !important;
}}

div[data-testid="stChatInput"] textarea {{
    background: #ffffff !important;
    color: #111827 !important;
    caret-color: #6366f1 !important;
    font-size: 0.92rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 13px 14px !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    resize: none !important;
    line-height: 1.5 !important;
}}

div[data-testid="stChatInput"] textarea::placeholder {{
    color: #9ca3af !important;
    font-weight: 400 !important;
}}

/* Submit button — soft grey, looks like a gentle send icon not a CTA */
div[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] {{
    background: #e5e7eb !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    margin: 6px 8px 6px 0 !important;
    box-shadow: none !important;
    transition: background .15s ease, border-color .15s ease !important;
    opacity: 0.75;
}}

div[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"] svg {{
    color: #9ca3af !important;
    fill: #9ca3af !important;
}}

div[data-testid="stChatInput"] button[data-testid="stChatInputSubmitButton"]:hover {{
    background: #d1d5db !important;
    border-color: #9ca3af !important;
    opacity: 1;
}}

/* When input has content, make button slightly more visible */
div[data-testid="stChatInput"]:focus-within button[data-testid="stChatInputSubmitButton"] {{
    background: #e5e7eb !important;
    opacity: 0.9;
}}

div[data-testid="stChatInput"]:focus-within {{
    border-color: #a5b4fc !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.10), 0 1px 4px rgba(0,0,0,0.05) !important;
}}

/* Spinner */
.stSpinner > div {{ border-top-color: #6366f1 !important; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: #d1d5db; border-radius: 2px; }}
</style>

<div id="ac-topbar">
    <img class="ac-logo" src="data:image/png;base64,{LOGO_B64}" alt="AdCopilot logo">
    <span class="ac-name">AdCopilot</span>
    <div class="ac-sep"></div>
    <span class="ac-sub">AI SaaS Ad Strategy &nbsp;·&nbsp; Budget allocation &nbsp;·&nbsp; Audience targeting &nbsp;·&nbsp; Campaign performance</span>
</div>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_run" not in st.session_state:
    st.session_state.last_run = None


# ── Helpers ───────────────────────────────────────────────────────────────
def stream_response(text: str):
    words = text.split(" ")
    out, ph = "", st.empty()
    for word in words:
        out += word + " "
        ph.markdown(out)
        time.sleep(0.01)
    return out.strip()


def is_followup(q: str) -> bool:
    terms = ["that","this","those","them","it","previous","above","same",
             "again","what about","how about","compare with","why","also"]
    q = q.lower()
    return any(t in q for t in terms)


def build_query(current: str) -> str:
    if not st.session_state.messages or not is_followup(current):
        return current
    ctx = "\n\nPrevious conversation:\n"
    for m in st.session_state.messages[-4:]:
        ctx += f"{m['role'].upper()}: {m['content']}\n"
    return f"{ctx}\nFollow-up: {current}"


# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    if st.button("+ New Analysis", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_run = None
        st.rerun()

    st.markdown('<div class="sb-label">Model</div>', unsafe_allow_html=True)
    model_name = st.selectbox("Model", ["mistral", "llama3"], label_visibility="collapsed")

    st.markdown('<div class="sb-label">Prompt Strategy</div>', unsafe_allow_html=True)
    prompt_strategy = st.selectbox("Strategy", ["baseline", "meta", "meta_reflect"],
                                   label_visibility="collapsed")

    st.markdown('<div class="sb-label">Options</div>', unsafe_allow_html=True)
    use_cache = st.checkbox("Enable response cache", value=True)

    st.markdown("---")

    st.markdown('<div class="sb-label">Web Search</div>', unsafe_allow_html=True)
    web_search_mode = st.selectbox("Web search", ["mock", "tavily"],
                                   label_visibility="collapsed")

    st.markdown('<div class="sb-label">Tavily API Key</div>', unsafe_allow_html=True)
    tavily_api_key = st.text_input("Tavily key", type="password",
                                   placeholder="Optional",
                                   label_visibility="collapsed")

    if st.session_state.last_run:
        st.markdown("---")
        d = st.session_state.last_run
        c_cls = "hit" if d["cached"] else "miss"
        c_lbl = "Hit" if d["cached"] else "Miss"
        st.markdown(f"""
        <div class="sb-label">Last Run</div>
        <div class="run-card">
          <div class="run-row"><span class="run-lbl">Model</span><span class="run-val">{d['model']}</span></div>
          <div class="run-row"><span class="run-lbl">Strategy</span><span class="run-val">{d['strategy']}</span></div>
          <div class="run-row"><span class="run-lbl">Cache</span><span class="run-val {c_cls}">{c_lbl}</span></div>
          <div class="run-row"><span class="run-lbl">Time</span><span class="run-val">{d['time']}s</span></div>
        </div>""", unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div class="card-grid">
      <div class="s-card">
        <span class="s-card-label">Budget</span>
        <span class="s-card-text">Recommend budget allocation for a $50K B2B SaaS launch across LinkedIn, Google, and Meta.</span>
      </div>
      <div class="s-card">
        <span class="s-card-label">Audience</span>
        <span class="s-card-text">Which audience segment historically produced the highest ROI?</span>
      </div>
      <div class="s-card">
        <span class="s-card-label">Platform</span>
        <span class="s-card-text">Compare LinkedIn Ads and Google Ads performance for enterprise SaaS campaigns.</span>
      </div>
      <div class="s-card">
        <span class="s-card-label">Competitive</span>
        <span class="s-card-text">Analyze competitor messaging and keyword trends for AI productivity SaaS.</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

query = st.chat_input("Ask a SaaS ad strategy question...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    payload = {
        "query": query,
        "model_name": model_name,
        "prompt_strategy": prompt_strategy,
        "use_cache": use_cache,
        "web_search_mode": web_search_mode,
        "tavily_api_key": tavily_api_key.strip() if tavily_api_key else None
    }

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            try:
                resp = requests.post(API_URL, json=payload, timeout=180)
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data["response"]["response"]
                    final = stream_response(answer)
                    st.session_state.messages.append({"role": "assistant", "content": final})
                    st.session_state.last_run = {
                        "model":    data.get("model_name", model_name),
                        "strategy": data.get("prompt_strategy", prompt_strategy),
                        "cached":   data["response"].get("cached", False),
                        "time":     data["response"].get("response_time_sec", 0)
                    }
                    st.rerun()
                else:
                    err = f"Backend error {resp.status_code}. Run: uvicorn app:app --reload"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})
            except requests.exceptions.ConnectionError:
                err = "Cannot reach backend. Run: uvicorn app:app --reload"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
            except Exception as e:
                err = f"Error: {e}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})
