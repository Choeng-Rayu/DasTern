# DasTern Architecture

## Overview
DasTern is a modular OCR + AI system for medical prescriptions with four services:

- **Mobile Flutter App**: User interface for capture and review
- **Next.js Backend**: API gateway, auth, workflow, database
- **OCR Service**: Image preprocessing + Tesseract OCR
- **AI LLM Service**: MT5-based correction + chatbot

## Core Principles
- **Separation of concerns** (OCR vs AI vs orchestration vs UI)
- **Independent scaling** of OCR and AI services
- **Stateless processing** for OCR and AI
- **Clear API boundaries**

## Request Flow
1. Flutter uploads image to Next.js
2. Next.js sends image to OCR Service
3. OCR Service returns raw text
4. Next.js optionally calls AI LLM Service for correction
5. Next.js stores results and returns to Flutter
