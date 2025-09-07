# DB Load UI (Vite + React + Tailwind)

## Запуск локально
```
cd ui
npm install
npm run dev
```

Откроется http://localhost:5173

## Запуск в Docker
```
docker build -t db-load-ui ./ui
docker run -p 8081:80 db-load-ui
```
Откроется http://localhost:8081
