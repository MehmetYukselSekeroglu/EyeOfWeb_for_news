# Eye of Web for News

### RSS haber kaynakları için yüz tespiti, indeksleme ve benzerlik araması

**Yazar ve geliştirici: Mehmet Yüksel Şekeroğlu**

**Son güncelleme: 11 Kasım 2024**

Eye of Web for News, RSS beslemelerindeki haber sayfalarını tarayan, sayfalardaki
görsellerden yüz özellikleri çıkaran ve bu özellikleri PostgreSQL üzerinde saklayan
bir Python projesidir. Ayrı çalışan HTTP API, tek yüz içeren bir fotoğrafı kayıtlı
yüz vektörleriyle karşılaştırır ve ilgili haber kaynaklarını döndürür.

## İçindekiler

- [Özellikler](#özellikler)
- [Çalışma akışı](#çalışma-akışı)
- [Proje yapısı](#proje-yapısı)
- [Kurulum](#kurulum)
- [Yapılandırma](#yapılandırma)
- [Çalıştırma](#çalıştırma)
- [HTTP API](#http-api)
- [Veritabanı](#veritabanı)
- [Mevcut sınırlamalar](#mevcut-sınırlamalar)
- [Katkı ve telif](#katkı-ve-telif)

## Özellikler

- `rss.txt` içindeki kaynaklardan haber bağlantılarının toplanması.
- Haber sayfaları ve görsellerinin taranması; kaynak URL ve başlıklarının saklanması.
- InsightFace ile yüz tespiti, embedding, yaş ve cinsiyet tahmini.
- OpenCV ile görsel işleme ve NumPy ile kosinüs benzerliği hesabı.
- PostgreSQL üzerinde yüzler, görseller, alan adları ve sayfalar arasında ilişki kurulması.
- Flask ve Waitress tabanlı arama ve istatistik API'si.
- Yapılandırılabilir tarayıcı iş parçacığı sayısı ve ONNX Runtime sağlayıcıları.
- C ile yazılmış yardımcı istatistik aracı: `weKnow_stats_tool.c`.

## Çalışma akışı

```text
rss.txt → RSS haber bağlantıları → haber sayfası/görsel tarama
                                          ↓
                               InsightFace yüz analizi
                                          ↓
                             PostgreSQL: vektör + kaynak
                                          ↑
Fotoğraf → POST /search → yüz analizi → kosinüs karşılaştırması
                                          ↓
                              benzer yüzler + haber URL'leri
```

`main.py`, RSS listesi üzerinde sürekli çalışır. Her tur tamamlandığında 3600 saniye
bekler. `web_api.py` bağımsız bir süreçtir; tarayıcıyı kendisi başlatmaz.

## Proje yapısı

| Yol | Açıklama |
| --- | --- |
| `main.py` | RSS okuma ve haber tarama döngüsü |
| `web_api.py` | `/search` ve `/info` HTTP uçları |
| `rss.txt` | RSS kaynak listesi |
| `requirements.txt` | Python bağımlılık listesi |
| `lib/make_config.py` | Yerel yapılandırma üreticisi |
| `lib/init_insightface.py` | Yüz analiz modelinin hazırlanması |
| `lib/signle_page_crawler.py` | Haber sayfası tarayıcısı; dosya adı bu biçimdedir |
| `lib/database_toolkit.py` | Veritabanı bağlantısı ve veri işlemleri |
| `lib/downloaders/` | Görsel indirme yardımcıları |
| `lib/output/` | Konsol çıktıları ve başlıklar |
| `sql/postgresql_schema.sql` | PostgreSQL tablo şeması |
| `linux.sh` | Docker/PostgreSQL yönetim yardımcı komutları |
| `weKnow_stats_tool.c` | libpq ve cJSON kullanan istatistik aracı |

## Kurulum

Komutları depo kök dizininde çalıştırın. Python ortamına ek olarak PostgreSQL ve
kullanılan görüntü işleme paketlerinin sistem derleme bağımlılıkları gerekir.
`web_api.py`, `imghdr` kullandığından Python 3.13 ve üzeriyle doğrudan uyumlu değildir.

```bash
git clone https://github.com/MehmetYukselSekeroglu/EyeOfWeb_for_news.git
cd EyeOfWeb_for_news
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
# Kaynak kodda kullanılan, mevcut listede bulunmayan ek bağımlılıklar:
python -m pip install feedparser waitress numba
```

Bağımlılıklar sürüm kilidi içermemektedir. Listede hem `onnxruntime` hem de
`onnxruntime-gpu` vardır; hedef ortamda kullanılacak sağlayıcı ve paket uyumu ayrıca
doğrulanmalıdır. Model dosyalarının ilk kullanımda indirilmesi gerekebilir.

### Yapılandırma dosyasını üretme

```bash
python -m lib.make_config
```

Bu komut `config/config.json` dosyasını oluşturur. Mevcut dosyanın üzerine
yazabildiğinden özelleştirilmiş yapılandırmayı yeniden üretmeden önce yedekleyin.

## Yapılandırma

| Alan | Kullanım |
| --- | --- |
| `database_config` | PostgreSQL veritabanı, kullanıcı, parola, sunucu ve port |
| `service.thread` | Tarayıcı iş parçacığı sayısı; varsayılan `4` |
| `service.save_images` | Görsellerin saklanmasıyla ilgili seçenek |
| `web_requests.timeout` | İstek zaman aşımı; varsayılan `10` |
| `web_requests.ssl_verification` | TLS sertifika doğrulaması |
| `insightface.main.name` | Model adı; varsayılan `buffalo_l` |
| `insightface.main.providers` | ONNX Runtime yürütme sağlayıcıları |
| `insightface.prepare.ctx_id` | Model bağlamı; varsayılan `-1` |
| `insightface.prepare.det_size` | Yüz tespit giriş boyutu; varsayılan `[640, 640]` |
| `api_config.port` | HTTP portu; varsayılan `8080` |
| `api_config.localhost_only` | `true`: `127.0.0.1`, `false`: `0.0.0.0` üzerinde dinleme |

Yerel yapılandırmada gerçek veritabanı bilgilerini girin. `base_dir`, `temp_dir`,
`data_dir` ve `database_schema` alanları üretim anındaki çalışma dizinine göre
oluşturulur; projeyi taşıdıktan sonra bunları gözden geçirin.

### PostgreSQL şemasını yükleme

Veritabanı ve kullanıcı hazır olduğunda şemayı mevcut bağlantınıza uygulayın:

```bash
psql -h 127.0.0.1 -U postgres -d WebEye -f sql/postgresql_schema.sql
```

`linux.sh` ayrıca `--generate-docker`, `--prepare-psql`, `--start-container`,
`--stop-container` ve `--sql-shell` seçeneklerini içerir. Bu yardımcı betik `jq`,
Docker ve `sudo` kullanır. `--remove-container` seçeneği silme işlemi yapar.

## Çalıştırma

Yapılandırmayı ve veritabanını hazırladıktan sonra iki ayrı terminal kullanın:

```bash
# Terminal 1: RSS tarayıcısı
source .venv/bin/activate
python main.py
```

```bash
# Terminal 2: HTTP API
source .venv/bin/activate
python web_api.py
```

Yerel kullanım için `api_config.localhost_only` değerini `true` yapın. Varsayılan
şablonda bu değer `false` olduğundan API tüm ağ arayüzlerinde dinler.

## HTTP API

Aşağıdaki örnekler yerel `8080` portunu kullanır. JSON çıktıları temsilidir.

### `GET /info`

Veritabanındaki kayıt sayılarını döndürür.

```bash
curl http://127.0.0.1:8080/info
```

```json
{
  "success": true,
  "message": "Proccess successfuly",
  "domain_count": 12,
  "face_count": 345,
  "image_hash_count": 210,
  "email_count": 0,
  "url_path_count": 180,
  "url_pathetc_count": 35,
  "total_combination": 345
}
```

### `POST /search`

Görseli `multipart/form-data` isteğinin `target` alanıyla gönderin. Görselde tam
olarak bir yüz bulunmalıdır. Mevcut yükleme sınırı 7 MiB'dir; `.png`, `.jpg` ve
`.jpeg` kullanın.

```bash
curl -X POST http://127.0.0.1:8080/search -F 'target=@ornek.jpg'
```

```json
{
  "success": true,
  "message": "Proccess successfuly",
  "took": 0.56,
  "data": [
    {
      "similarity": 85.42,
      "deceted_url": "https://example.com/haber/123",
      "image_url": "https://example.com/gorsel.jpg",
      "age": 35,
      "gender": "Male",
      "detection_score": 0.98,
      "detection_date": "2024-11-11T12:00:00",
      "image": "base64_encoded_image_data",
      "title": "Örnek haber başlığı"
    }
  ]
}
```

`deceted_url`, `url_pathetc_count` ve `Proccess successfuly` yazımları mevcut API
sözleşmesinden alınmıştır. İstemci yazarken bu alan adlarını aynen kullanın.
Arama kodu, benzerlik yüzdesi `35` değerinden büyük kayıtları değerlendirir ve en
fazla 30 sonuç döndürür. Bu değer bir kimlik doğrulama güvencesi değildir.
Eşleşme yoksa `data` boş listedir; sıfır veya birden fazla yüz varsa `success: false`
yanıtı döner.

## Veritabanı

- `FaceStorageID`: Yüz vektörü ve tespit bilgileri.
- `ImageBasedMain`: Görseller ile yüz/kaynak kayıtlarının ilişkileri.
- `PageBasedMain`: Taranan sayfa bilgileri.
- `BaseDomainID`, `UrlPathID`, `UrlEtcID`: Kaynak adreslerinin bileşenleri.
- `ImageHashID`, `ImageTitleID`: Görsel özeti ve başlığı.
- `EmailAddressID`, `CrawledAddress`: Yardımcı adres ve tarama kayıtları.

Tam alanlar ve ilişkiler için `sql/postgresql_schema.sql` dosyasına bakın.

## Mevcut sınırlamalar

- API kodunda kimlik doğrulama ve istek hız sınırlaması bulunmaz.
- Arama, kayıtlı yüzleri Python tarafında tek tek karşılaştırır; büyük veri
  kümelerinde maliyet artar.
- API yükleme uzantı listesinde `.wepm` yazımı bulunur; bu, WebP desteğinin
  doğrulandığı anlamına gelmez.
- `linux.sh` içindeki `--saasd` bölümü tamamlanmamıştır ve depoda bulunmayan
  `php_client/` dizinine atıf yapar; süreçleri yukarıdaki gibi ayrı başlatın.
- Bu README, canlı PostgreSQL/model/GPU entegrasyon testinin yapıldığını iddia etmez.
- Yüz benzerliği, yaş ve cinsiyet çıktıları model tahminleridir; kesin kimlik
  tespiti olarak değerlendirilmemelidir.

Yerel parolaları, yapılandırmaları, toplanmış görselleri, yüz vektörlerini ve
veritabanı yedeklerini Git deposuna eklemeyin. Veri toplama ve işleme süreçlerinde
ilgili kişisel veri yükümlülüklerini ve kaynakların kullanım koşullarını gözetin.

## Katkı ve telif

**Yazar: Mehmet Yüksel Şekeroğlu**

Hata bildirimlerinde yeniden üretme adımlarını, kullanılan ortamı ve kişisel veri
veya parola içermeyen hata çıktısını paylaşın. Katkılarda değişikliğin amacını ve
yapılan kontrolleri açıklayın.

© Mehmet Yüksel Şekeroğlu. Tüm hakları saklıdır.
Depoda ayrı bir açık kaynak lisansı bulunmamaktadır; herkese açık erişim tek başına
kullanım, dağıtım veya yeniden lisanslama izni vermez.
