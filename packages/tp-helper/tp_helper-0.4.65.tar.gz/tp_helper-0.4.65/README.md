# TP Helper

Collection of common practices used in Transpropusk's projects.


## Установка:
`poetry add tp-helper`

## Очистка при обновлении
- `poetry cache clear --all PyPI`
- `poetry add tp-helper`
- `poetry update`


```
poetry cache clear pypi --all --no-interaction; poetry add tp-helper@latest
```

```
poetry cache clear pypi --all --no-interaction && poetry add tp-helper@latest
```



## Публикация:
Собирает и загружает собранный пакет в PyPI.
`poetry publish --build`