#!/bin/bash

echo "=== WebSocket Load Testing ==="
echo "Этот скрипт поможет запустить тестирование"
echo ""

echo "1. Запуск WebSocket сервера в фоне..."
python3 websocket.py &
SERVER_PID=$!
sleep 2

echo "2. Запуск нагрузочного тестирования..."
echo "   (Тест будет идти 60 секунд)"
artillery run test_config.yml &
ARTILLERY_PID=$!

echo ""
echo "3. Мониторинг (нажмите Ctrl+C для остановки):"
echo "   - htop (CPU/память) - откройте в другом терминале"
echo "   - bmon (сеть) - откройте в другом терминале"
echo ""
echo "Для мониторинга откройте дополнительные терминалы:"
echo "docker exec -it websocket_load_test htop"
echo "docker exec -it websocket_load_test bmon"
echo ""

# Ждем завершения Artillery
wait $ARTILLERY_PID

echo ""
echo "4. Завершение тестирования..."
kill $SERVER_PID
echo "Тестирование завершено!" 