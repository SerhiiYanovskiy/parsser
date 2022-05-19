Account format:
    For On Join Parser (Check on join messages):
        TYPE(0 = Send Message, 1 = Parse):TOKEN:USE_PROXY(0 = Do Not Use, 1 = Use)
        Example:
            0:OTQ1NTI3MjE0NTIxMzUyMjUz.YhRdVA.mkhThCXMPeWPDawotRS3MBP1jfM:0
            1:OTQ1NTI3MjE0NTIxMzUyMjUz.YhRdVA.mkhThCXMPeWPDawotRS3MBP1jfM:0
            0:OTQ1NTI3MjE0NTIxMzUyMjUz.YhRdVA.mkhThCXMPeWPDawotRS3MBP1jfM:1
            1:OTQ1NTI3MjE0NTIxMzUyMjUz.YhRdVA.mkhThCXMPeWPDawotRS3MBP1jfM:1
    For Member Parser (Parse all members):
        TYPE(0 = Send Message, 1 = Parse):TOKEN:USE_PROXY(0 = Do Not Use, 1 = Use):GUILD_ID:CHANNEL_ID
        Example:
            0:OTQ1NTI3MjE0NTIxMzUyMjUz.YhRdVA.mkhThCXMPeWPDawotRS3MBP1jfM:0
            1:OTQ1NTI3MjE0NTIxMzUyMjUz.YhRdVA.mkhThCXMPeWPDawotRS3MBP1jfM:0:641982223846866944:641983319256334366
            0:OTQ1NTI3MjE0NTIxMzUyMjUz.YhRdVA.mkhThCXMPeWPDawotRS3MBP1jfM:1
            1:OTQ1NTI3MjE0NTIxMzUyMjUz.YhRdVA.mkhThCXMPeWPDawotRS3MBP1jfM:1:641982223846866944:641983319256334366

Proxy format:
    PROXY_URL
    Example:
        http://login:pass@address:port - right
        http://address:port - right
        address:port - !!! NOT right
        login:pass@address:port - !!! NOT right

Messages format:
    GUILD_ID:MESSAGE
    Example:
        641982223846866944:{user} hello!
        641982223846866123:How are you?

Info:
    1) a) For On Join Parser you do not need to add guild IDs to the configuration, just connect to the server from the account you use for parse and enable notifications from the server
    1) b) For Member Parser you need add guild id and id of main chat to accounts file
    2) Proxy mast be http
    3) All bots must be join to similar servers
    4) Bad tokens (banned, etc.) will be saved in a file named "bad_tokens.txt"
    5) You can use 1 account for many guilds, add this token like new account but with another guild id
    6) One line in file "messages.txt" it's one message, bot choose random message from all messages in file

How to use:
    You must have Python 3+
    For install all libraries use command "pip install -r requirements.txt"
    Add accounts to file "accounts.txt"
    Add proxy to file "proxy.txt" if you use proxy
    The code is configured via a file "config.py"
    For start code use command "python main.py"
