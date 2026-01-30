# CTF Cicada-3301 Vol:1 – Writeup
# Welcome!

- YØ! I tackled **Cicada-3301 Vol:1** on TryHackMe ([link here](https://tryhackme.com/room/cicada3301vol1)), which was a **medium difficulty challenge**. It’s a mix of cryptography, steganography, audio analysis, and a bit of hash cracking.

In this writeup, I’ll show you my process, the tools I used, the mistakes I made (because yes, there were some, I'm human), and a few little victories along the way. Hope you find it useful and maybe a bit fun to read.

![COVER](../../assets/rooms/Cicada-3301-Vol%3A1/0.png)

## Task 1

**Description:**
"Hello, We are looking for highly intelligent individuals. To find them, we have devised a test. There is a message hidden in this image. Download and unzip the folder given to begin. Good Luck -3301"

**Info:**
Download and unzip the provided folder.

**Answer:** No answer needed

---

## Task 2 – Analyze the Audio

**Description:**
"Web Browsers are useless here. Welcome. Good Luck -3301. Use Sonic Visualizer to analyze the audio"

**Explanation:**
Sonic Visualizer is a tool for audio analysis, including creating spectrograms to visualize hidden frequencies and patterns. For this CTF, I used an online spectrogram tool instead of installing the software: [Audio Spectrogram Creator](https://convert.ing-now.com/audio-spectrogram-creator/).

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/2.png)

Then, I scanned the QR code found in the spectrogram using: [QR Scanner](https://qrscanner.net/).

Well...The QR code revealed a link!

**Question:** What is the link inside of the audio?

**Answer:** [https://pastebin.com/wphPq0Aa](https://pastebin.com/wphPq0Aa)

In the Pastebin we found a passphrase and a key:

* Passphrase: `SG01Ul80X1A0NTVtaHA0NTMh`
* Key: `Q2ljYWRh`

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/3.png)

---

## Task 3 – Decrypt the Passphrase and Key

**Description:**
"Use various encryption methods and ciphers to decode the passphrase and access the metadata of Welcome.jpg"

**Info:** Find and Decrypt the passphrase and key

**Answer:** No answer needed

**Explanation:**
The passphrase looks like Base64 (its length is a multiple of 4, which is typical for Base64). To decode it in the terminal:

```bash
echo 'SG01Ul80X1A0NTVtaHA0NTMh' | base64 --decode
echo 'Q2ljYWRh' | base64 --decode
```

**Question:** What is the decrypted passphrase?

* **Decrypted Passphrase:** `Hm5R_4_P455mhp453!`

**Question:** What is the decrypted key?

* **Decrypted Key:** `Cicada`

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/4.png)

---

**Info:** Still looks funny? Find and use a cipher along with the key to decipher the passphrase

Later, we needed to combine passphrase and key using a cipher. I tried several combinations that produced errors until I remembered simplicity might be the answer. After some time playing with CyberChef, the correct method was Vigenère with encoding:

**Question:** What is the final passphrase?

* **Final Passphrase:** `Ju5T_4_P455phr453!`

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/5.png)

---

## Task 4 – Steganography on Welcome.jpg

**Description:**
"Use Steganography tools to gather metadata from Welcome.jpg as well as find the hidden message inside of the image file. Using the found passphrase along with Stego tools find the secret message."

**Info:** Using the found passphrase along with Stego tools find the secret message

**Answer:** No answer needed

I used `steghide` to extract content from the image using the passphrase from Task 3:

```bash
steghide extract -sf welcome.jpg
```

* `-sf` specifies the source file for extraction.

**Result:**
Extracted a file called `invitation`, containing a link: https://imgur.com/a/c0ZSZga

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/6.png)

**Question:** What link is given?

**Answer:** [https://imgur.com/a/c0ZSZga](https://imgur.com/a/c0ZSZga)

---

## Task 5 – Hidden Files Inside the Image

**Description:**
"I am surprised you have made it this far... I doubt you will make it any further. -3301. Use Stego tools to find the hidden files inside of the image"

**Info:** Using stego tools find the hidden file inside of the image

**Answer:** No answer needed

**Explanation:**
Well, I tried `steghide` again, no luck... then `exiftool`, still nothing.
I couldn't resist and checked a hint: 

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/7.png)
![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/8.png)

"Use the same tool used to extract data in the original Cicada challenges"

Since we have a JPEG, Outguess seemed a good bet.

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/9.png)

```bash
outguess -r 8S8OaQw.jpg binhoBerde
```

**Result:**
Hidden message found inside the file.

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/10.png)

**Question:** What tool did you use to find the hidden file?

**Answer:** Outguess

---

## Task 6 – Crack the Hash

**Description:**
"We have one last challenge to find our individuals. Find the last clue, crack the hash, decipher the message. Good Luck -3301"

**Info:** Crack the Hash

**Answer:** No answer needed

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/11.png)
![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/16.png)

**Explanation:**
The file contained a hash inside and some intructions for a puzzle:

```
b6a233fb9b2d8772b636ab581169b58c98bd4b8df25e452911ef75561df649edc8852846e81837136840f3aa453e83d86323082d5b6002a16bc20c1560828348
```

**Question:** What is the Hash type? (hash-identifier AKA: my eyes)

* **Answer:** sha512

**Question:** What is the Link from the hash?

Using online tools (md5hashing.net), I cracked it and got another Pastebin link:

**Answer:** [https://pastebin.com/6FNiVLh5](https://pastebin.com/6FNiVLh5)

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/15.png)

**Info:** Decipher the message

**Answer:** No answer needed | man, this thing was boooooooooring.

**Question:** What is the link?
After reading the Pastebin (very philosophical/random, excerpts from *Liber AL vel Legis* and solving the puzzle), the clue we needed pointed to a shortened URL:
![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/17.png)
*Desperation leads a man to use paint instead of python*

**Answer:** [https://bit.ly/39pw2NH](https://bit.ly/39pw2NH)

---

## Task 7 – Song Linked

**Description:** "Find the song linked"

**Explanation:**
The shortened Pastebin URL led to SoundCloud. Weird, but that’s the final step.

**Question:** What is the song linked?

**Answer:** The Instar Emergence

![IMAGE](../../assets/rooms/Cicada-3301-Vol%3A1/18.png)

# Goodbye!

That’s it for my writeup! I had a lot of fun, learned a ton, and hopefully this gives you some insight into tackling Cicada-style puzzles. Until next time and keep hacking!

<p align="center">
  <img src="../../assets/vault/edward.png" alt="Edward" width="400"/>
</p
