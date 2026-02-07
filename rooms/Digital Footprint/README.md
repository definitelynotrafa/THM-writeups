# Digital Footprint – Writeup
# Welcome!

- YØ! I tackled **Digital Footprint** on TryHackMe, which was a challenge focused on **OSINT** (Open Source Intelligence). This room is all about investigating a company called ACME Jet Solutions through analyzing images, metadata, and archived web content to uncover their real history.

In this writeup, I'll show you my investigative process, the tools I used for metadata analysis and web archaeology, and how I tracked down the truth about this mysterious company!

---

## Task 1 – Photo Location Analysis

**Description:**
An ACME Jet Solutions employee uploaded a photo of a residential property believed to be linked to ACME Jet's early operations. Can you figure out where the picture was taken to confirm or debunk the rumour?

**Flag format:** `THM{City}`

**Question:** In which city was the photo taken?

### Investigation

First, I examined the photo provided. Right away, I spotted something interesting in the image: text saying **"The Rectory"**.

![IMAGE](../../assets/rooms/Digital%20Footprint/foto1.png)

My first instinct was to search for "The Rectory" on Google. I found The Rectory Hotel in the United Kingdom.

![IMAGE](../../assets/rooms/Digital%20Footprint/foto2.png)

However, submitting the UK city as the answer didn't work. Time to do what I should have done first: **check the metadata**!

![IMAGE](../../assets/rooms/Digital%20Footprint/foto3.png)

Perfect! I found GPS coordinates in the metadata:

```
26 deg 12' 14.76", 28 deg 2' 50.28"
```

Throwing these coordinates into Google Maps revealed the actual location...

![IMAGE](../../assets/rooms/Digital%20Footprint/foto4.png)

**Answer:** `THM{Johannesburg}`

---

## Task 2 – Website Archaeological Investigation

**Description:**
ACME Jet Solutions (warc-acme.com/jef/) is all over social media claiming they were founded in 2025 and that they're the fastest-growing data company in Africa. But something doesn't add up—one of their ex-employees ensures you that the company existed long before that.

Your job as an OSINT investigator is to verify their founding date using only public information.

**Flag Format:** `THM{YYYYMMDDHHMMSS}`

**Question:** When was the website first published on the internet?

### Investigation

Visiting `warc-acme.com/jef/` directly didn't work—the page just doesn't load. But wait... when investigating the history of websites, there's a perfect tool for this: **Wayback Machine**!

![IMAGE](../../assets/rooms/Digital%20Footprint/asset.png)

Well, well, well... look who was already on the internet back in **2016**!

![IMAGE](../../assets/rooms/Digital%20Footprint/foto5.png)

The Wayback Machine shows the exact timestamp when this website was first archived. We can see the **FirstFileDate** which gives us our answer:

![IMAGE](../../assets/rooms/Digital%20Footprint/foto6.png)

**Answer:** `THM{20160210224602}`

So much for being founded in 2025! The company's web presence dates back to February 10, 2016, at 22:46:02.

---

## Task 3 – Landmark Identification

**Description:**
Further investigation uncovers another image believed to be connected to the company's international expansion.

Research reveals that to the right of the iconic landmark is a building that played a big role in the fight for independence of a particular country. Signs on the external wall provide the name of the building.

Submit the name of the building translated into English as the flag.

**Flag format:** `THM{Landmark}`

**Question:** What is the name of the building?

### Investigation

*[Investigation pending]*

**Answer:** `THM{?}`

---

## Takeaways

This challenge reinforces several key OSINT principles:

1. **Check metadata first** – Images often contain GPS coordinates and timestamps that can pinpoint exact locations
2. **Use the Wayback Machine** – Companies can't hide their digital history when it's been archived
3. **Don't trust surface-level information** – Always verify claims with multiple sources
4. **Reverse image search and landmark identification** are crucial OSINT skills

Great challenge for practicing fundamental OSINT techniques! 🔍
