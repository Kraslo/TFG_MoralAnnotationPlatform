# Diff Details

Date : 2025-12-30 16:39:58

Directory /home/kraslo/TFG/code/fetcher/src

Total : 34 files,  134 codes, 24 comments, 31 blanks, all 189 lines

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [src/tfg\_fetcher/\_\_init\_\_.py](/src/tfg_fetcher/__init__.py) | Python | 1 | 4 | 2 | 7 |
| [src/tfg\_fetcher/app/\_\_init\_\_.py](/src/tfg_fetcher/app/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/tfg\_fetcher/app/main.py](/src/tfg_fetcher/app/main.py) | Python | 71 | 5 | 8 | 84 |
| [src/tfg\_fetcher/handlers/\_\_init\_\_.py](/src/tfg_fetcher/handlers/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/tfg\_fetcher/handlers/fuseki\_handler.py](/src/tfg_fetcher/handlers/fuseki_handler.py) | Python | 58 | 3 | 13 | 74 |
| [src/tfg\_fetcher/handlers/postgre1\_handler.py](/src/tfg_fetcher/handlers/postgre1_handler.py) | Python | 22 | 7 | 6 | 35 |
| [src/tfg\_fetcher/models/\_\_init\_\_.py](/src/tfg_fetcher/models/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/tfg\_fetcher/models/models.py](/src/tfg_fetcher/models/models.py) | Python | 44 | 2 | 15 | 61 |
| [src/tfg\_fetcher/services/\_\_init\_\_.py](/src/tfg_fetcher/services/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/tfg\_fetcher/services/fetch\_news.py](/src/tfg_fetcher/services/fetch_news.py) | Python | 59 | 26 | 19 | 104 |
| [src/tfg\_fetcher/services/insert\_annotations.py](/src/tfg_fetcher/services/insert_annotations.py) | Python | 59 | 14 | 18 | 91 |
| [src/tfg\_fetcher/services/insert\_fuseki.py](/src/tfg_fetcher/services/insert_fuseki.py) | Python | 268 | 29 | 58 | 355 |
| [src/tfg\_fetcher/services/llm\_service.py](/src/tfg_fetcher/services/llm_service.py) | Python | 46 | 11 | 11 | 68 |
| [src/tfg\_fetcher/services/moral\_annotations.py](/src/tfg_fetcher/services/moral_annotations.py) | Python | 30 | 21 | 13 | 64 |
| [src/tfg\_fetcher/utils/\_\_init\_\_.py](/src/tfg_fetcher/utils/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [src/tfg\_fetcher/utils/article\_processing.py](/src/tfg_fetcher/utils/article_processing.py) | Python | 19 | 3 | 7 | 29 |
| [src/tfg\_fetcher/utils/logging\_config.py](/src/tfg_fetcher/utils/logging_config.py) | Python | 40 | 1 | 9 | 50 |
| [src/tfg\_fetcher/utils/moral\_annotation.py](/src/tfg_fetcher/utils/moral_annotation.py) | Python | 108 | 75 | 32 | 215 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/app/\_\_init\_\_.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/app/__init__.py) | Python | 0 | 0 | -1 | -1 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/app/main.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/app/main.py) | Python | -71 | -3 | -8 | -82 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/handlers/\_\_init\_\_.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/handlers/__init__.py) | Python | 0 | 0 | -1 | -1 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/handlers/fuseki\_handler.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/handlers/fuseki_handler.py) | Python | -45 | -3 | -14 | -62 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/handlers/postgre1\_handler.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/handlers/postgre1_handler.py) | Python | -22 | -7 | -6 | -35 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/models/\_\_init\_\_.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/models/__init__.py) | Python | 0 | 0 | -1 | -1 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/models/models.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/models/models.py) | Python | -27 | -2 | -13 | -42 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/services/\_\_init\_\_.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/services/__init__.py) | Python | 0 | 0 | -1 | -1 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/services/fetch\_news.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/services/fetch_news.py) | Python | -46 | -21 | -15 | -82 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/services/insert\_annotations.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/services/insert_annotations.py) | Python | -69 | -14 | -16 | -99 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/services/insert\_fuseki.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/services/insert_fuseki.py) | Python | -181 | -21 | -44 | -246 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/services/llm\_service.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/services/llm_service.py) | Python | -31 | -10 | -7 | -48 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/services/moral\_annotations.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/services/moral_annotations.py) | Python | -34 | -17 | -12 | -63 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/utils/article\_processing.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/utils/article_processing.py) | Python | -19 | -3 | -6 | -28 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/utils/logging\_config.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/utils/logging_config.py) | Python | -38 | -1 | -8 | -47 |
| [/mnt/c/Users/ignacio.escribano\_bl/OneDrive/TFG/code/fetcher/src/utils/moral\_annotation.py](//mnt/c/Users/ignacio.escribano_bl/OneDrive/TFG/code/fetcher/src/utils/moral_annotation.py) | Python | -108 | -75 | -32 | -215 |

[Summary](results.md) / [Details](details.md) / [Diff Summary](diff.md) / Diff Details