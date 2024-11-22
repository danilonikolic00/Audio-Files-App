## Audio-Files-App
**Projekat iz predmeta Napredno Softversko Inženjerstvo**  

Desktop aplikacija kreirana korišćenjem programskog jezika **Python**, frejmvorka **FFmpeg**, kao i python biblioteka **FFmpeg**, **ttkbootstrap**, **Tkinter**, i **PIL**.  

Aplikacija omogućava rad sa audio fajlovima različitih formata, pružajući funkcionalnosti kao što su konverzija, kompresija, trimovanje i spajanje audio fajlova.
Postoji mogućnost prikaza detalja o kompresovanom fajlu, kao i vizuelne informacije o njemu (prikaz spektograma).
Pored toga, moguće je editovati metapodatke fajla, promeniti detalje zvuka (brzina reprodukcije i glasnoća), a postoji mogućnost ekstrakcije zvuka iz video fajla. 

---

## Sadržaj

- [Tehnologije](#tehnologije)
- [FFmpeg](#FFmpeg)
- [Instalacija](#instalacija)
- [Funkcionalnosti](#funkcionalnosti)
  - [1. Konverzija](#1-konverzija)
  - [2. Kompresija](#2-kompresija)
  - [3. Trim](#3-trim)
  - [4. Merge](#4-merge)
  - [5. Editovanje Fajla](#5-edit)
  - [6. Podešavanje Osnovnih Parametara](#6-podešavanje-osnovnih-parametara)
  - [7. Prikaz Dodatnih Informacija](#7-prikaz-dodatnih-informacija)
  - [8. Ekstrakcija zvuka iz video fajla](#8-ekstrakcija-zvuka-iz-video-fajla)

---

## Tehnologije

**Python**: Programski jezik.
**FFmpeg**: Obrada i konverzija audio fajlova.
**Tkinter & ttkbootstrap**: Za korisnički interfejs.
**PIL**: Rad sa slikama (prikaz spektrograma).

## Instalacija

Pre nego što pokrenete aplikaciju, potrebno je instalirati:  
1. **Visual Studio Code**: [Preuzmite ovde](https://code.visualstudio.com/download)  
2. **FFmpeg**: [Preuzmite ovde](https://www.ffmpeg.org/download.html)  
3. **Python**: [Preuzmite ovde](https://www.python.org/downloads/)  
4. **Prateće biblioteke**: Instalacija putem PIP-a:  
   ``` bash
   pip install ffmpeg
   pip install tkinter
   pip install ttkbootstrap
   pip install pillow
**Napomena**: FFmpeg nakon instalacije mora da bude dodat u *PATH*

---

## FFmpeg

**FFmpeg** je open-source softverski alat za snimanje, konverziju i strimovanje multimedijalnih fajlova. Podržava veliki broj audio, video i formata slika, što ga čini standardom u svetu obrade multimedije.

**Glavne karakteristike uključuju:**

- Konverziju između različitih formata (npr. MP3, WAV, FLAC, AAC za audio, ili MP4, MKV za video).
- Manipulaciju zvuka i videa (promena bitrate-a, sample rate-a, trimovanje, ekstrakcija zvuka iz videa).
- Visoke performanse i efikasnost u obradi velikih fajlova.

FFmpeg je odabran za projekat zbog svoje izuzetne fleksibilnosti i moći u obradi multimedijalnih fajlova. 
On omogućava rad sa gotovo svim poznatim audio i video formatima, što ga čini idealnim za aplikaciju koja pruža funkcionalnosti poput konverzije, kompresije, ekstrakcije zvuka i drugih manipulacija nad audio fajlovima.
FFmpeg rešava problem interoperabilnosti između različitih multimedijalnih formata i pruža korisnicima alate za kompleksne operacije bez potrebe za dubokim tehničkim znanjem.

U ovom projektu, FFmpeg je integrisan kao alat za:

- Konverziju audio fajlova u različite formate.
- Kompresiju, omogućavajući korisnicima da smanje veličinu fajlova prilagođavanjem bitrate-a, sample rate-a i broja kanala.
- Ekstrakciju zvuka iz video fajlova, čime korisnici mogu dobiti kvalitetne audio fajlove direktno iz videa.
- Manipulaciju zvuka, poput trimovanja i spajanja više fajlova.
Integracija se postiže kroz Python biblioteku **ffmpeg**, koja olakšava izvršavanje FFmpeg komandi direktno iz aplikacije.

**Problem koji rešava**

Audio fajlovi često dolaze u različitim formatima i sa različitim parametrima (bitrate, sample rate, veličina fajla). Ručna obrada takvih fajlova može biti izazovna za korisnike bez tehničkog znanja. FFmpeg rešava ovaj problem tako što omogućava automatizovanu i efikasnu obradu multimedijalnih fajlova kroz jedan alat koji podržava širok spektar formata i funkcionalnosti.

Kombinovanjem FFmpeg mogućnosti sa jednostavnim korisničkim interfejsom, aplikacija pruža moćne alate za obradu audio fajlova čak i korisnicima bez tehničkog iskustva.

---

## Funkcionalnosti

# 1. Konverzija
- Korisnik može:
    - Izabrati fajlove za konverziju.
    - Odabrati željeni format i dodatne opcije (bitrate, sample rate, broj kanala).
- Klikom na Convert započinje proces konverzije. Napredak konverzije se prikazuje putem progres bara.

# 2. Kompresija
- Nakon konverzije, fajlovi se prikazuju u tabeli sa procentom kompresije.
- Duplim klikom na fajl pokreće se reprodukcija, dok desni klik prikazuje dodatne informacije.
- Opcije u tabeli fajlova:
    - Clear History: Briše sve fajlove iz tabele.
    - Clear Selected: Briše samo selektovane fajlove.

# 3. Trim
- Korisnik može trimovati fajl odabirom početka i kraja audio fajla.
- Klikom na Trim korisnik kreira novi fajl sa zadatim opsegom.

# 4. Merge
- Korisnik bira dva ili više fajlova istog formata.
- Klikom na Merge Files otvara se dijalog za unos imena i lokacije za čuvanje fajla.
- Nakon uspešnog spajanja, korisnik se obaveštava.

# 5. Edit
- Klikom na Edit File Info, korisnik može menjati:
    - Naslov (Title)
    - Album
    - Izvođač (Artist)
- Klikom na Apply, izmene se primenjuju na fajl.

# 6. Podešavanje Osnovnih Parametara
- Korisnik može menjati:
    - Brzinu reprodukcije: Od 0.5x do 1.5x.
    - Jačinu zvuka: Od -10dB do +10dB.
- Klikom na OK, generiše se novi fajl sa zadatim parametrima.

# 7. Prikaz Dodatnih Informacija
- Za izabrani fajl prikazuju se:
    - Trajanje
    - Kodek
    - Bitrate
    - Sample rate
    - Broj kanala
- Klikom na Show Spectrogram, generiše se spektrogram fajla kao vizuelni prikaz.

# 8. Ekstrakcija zvuka iz video fajla
- Korisnik može izabrati video fajl (npr. MP4, MKV, AVI).
- Nakon uspešne ekstrakcije generiše se audio fajl.

