.PHONY: help run-dev run-prod install-systemd install-nginx tls restart logs status clean health-check validate-paths

# Variables
DOMAIN ?= localhost
USER ?= talkbridge
REPO_PATH ?= /srv/talkbridge

help:
	@echo "TalkBridge Deployment Commands"
	@echo "=============================="
	@echo "Development:"
	@echo "  make run-dev          Run in development mode"
	@echo "  make run-prod         Run in production mode (local)"
	@echo ""
	@echo "Production Deployment:"
	@echo "  make install-systemd  Install systemd service"
	@echo "  make install-nginx    Install Nginx configuration"
	@echo "  make tls             Setup HTTPS with Let's Encrypt"
	@echo ""
	@echo "Management:"
	@echo "  make restart         Restart TalkBridge service"
	@echo "  make logs            Show service logs"
	@echo "  make status          Check service status"
	@echo "  make health-check    Test application health"
	@echo "  make clean           Clean up temporary files"
	@echo "  make validate-paths  Validate code for correct path usage"
	@echo ""
	@echo "Usage with custom domain:"
	@echo "  make install-nginx DOMAIN=mi-dominio.com"
	@echo "  make tls DOMAIN=mi-dominio.com"

run-dev:
	@echo "🚀 Starting TalkBridge in development mode..."
	conda activate talkbridge && python -m talkbridge.web --host=0.0.0.0 --port=8000 --debug

run-prod:
	@echo "🚀 Starting TalkBridge in production mode (local)..."
	conda activate talkbridge && python -m talkbridge.web \
		--host=127.0.0.1 \
		--port=8000

install-systemd:
	@echo "📦 Installing systemd service..."
	sudo cp talkbridge.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable talkbridge
	@echo "✅ Systemd service installed. Use 'make restart' to start."

install-nginx:
	@echo "🌐 Installing Nginx configuration for $(DOMAIN)..."
	sudo sed 's/<MI_DOMINIO>/$(DOMAIN)/g' nginx-talkbridge.conf > /tmp/talkbridge-nginx.conf
	sudo mv /tmp/talkbridge-nginx.conf /etc/nginx/sites-available/talkbridge
	sudo ln -sf /etc/nginx/sites-available/talkbridge /etc/nginx/sites-enabled/
	sudo nginx -t
	sudo systemctl reload nginx
	@echo "✅ Nginx configuration installed for $(DOMAIN)"

tls:
	@echo "🔒 Setting up HTTPS for $(DOMAIN)..."
	sudo certbot --nginx -d $(DOMAIN) --non-interactive --agree-tos --email admin@$(DOMAIN) || \
	(echo "❌ Automated certificate failed. Run manually:" && \
	 echo "sudo certbot --nginx -d $(DOMAIN)")

restart:
	@echo "🔄 Restarting TalkBridge service..."
	sudo systemctl restart talkbridge
	sudo systemctl status talkbridge --no-pager -l

logs:
	@echo "📋 TalkBridge service logs (last 50 lines):"
	sudo journalctl -u talkbridge -n 50 --no-pager

status:
	@echo "📊 TalkBridge service status:"
	sudo systemctl status talkbridge --no-pager -l

health-check:
	@echo "🏥 Checking application health..."
	@if command -v curl >/dev/null 2>&1; then \
		if curl -f -s -I http://localhost:8000 >/dev/null; then \
			echo "✅ Local health check passed (HTTP 200)"; \
		else \
			echo "❌ Local health check failed"; \
		fi; \
		if [ "$(DOMAIN)" != "localhost" ]; then \
			if curl -f -s -I https://$(DOMAIN) >/dev/null; then \
				echo "✅ External health check passed for https://$(DOMAIN)"; \
			else \
				echo "❌ External health check failed for https://$(DOMAIN)"; \
			fi; \
		fi; \
	else \
		echo "curl not available, cannot perform health check"; \
	fi

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .streamlit/logs/*
	@echo "✅ Cleanup completed"

validate-paths:
	@echo "🔍 Validating code path usage..."
	python tools/ci_guard_paths.py
	@echo "✅ Path validation completed"

# Deployment sequence
deploy: install-systemd install-nginx restart
	@echo "🎉 TalkBridge deployment completed!"
	@echo "Next steps:"
	@echo "1. Run 'make tls DOMAIN=<your-domain>' for HTTPS"
	@echo "2. Run 'make health-check' to verify deployment"
