# Phase 0: Project Scaffolding - Technical Implementation Plan

## Objective
Establish the foundational project structure, initializing both the Next.js frontend and the FastAPI backend, and verify communication between the two components.

## 1. Directory Structure Setup
Based on the `docs/grand-design.md`, the root project should contain `frontend/` and `backend/` directories.

## 2. Backend Initialization (`uv` + FastAPI)

1. **Initialize the Python project:**
   Navigate into `backend/` and initialize it with `uv`.
   ```bash
   cd backend
   uv init
   ```

2. **Install Core Dependencies:**
   ```bash
   uv add fastapi uvicorn pydantic python-dotenv
   ```

3. **Set up Application Structure:**
   Create the necessary scaffold outlined in the design document.
   ```bash
   mkdir app
   mkdir app/database app/models app/services app/utils
   type nul > .env
   type nul > app/main.py
   type nul > app/config.py
   ```

4. **Implement "Hello World" Endpoint (`app/main.py`):**
   ```python
   from fastapi import FastAPI

   app = FastAPI(title="Smart Traffic CCTV API")

   @app.get("/health")
   async def health_check():
       return {"status": "ok", "message": "Backend is running!"}
   ```

## 3. Frontend Initialization (`pnpm` + Next.js)

1. **Initialize Next.js Project:**
   From the root directory, create the Next.js application using `pnpm`. Use App Router and setup `src/` directory.
   ```bash
   pnpm create next-app@latest frontend \
     --typescript \
     --tailwind \
     --eslint \
     --app \
     --src-dir \
     --import-alias "@/*" \
     --use-pnpm
   ```

2. **Setup `shadcn/ui`:**
   Navigate into `frontend/` and initialize shadcn.
   ```bash
   cd frontend
   pnpm dlx shadcn-ui@latest init -y
   ```
   Add a couple of base components to test with:
   ```bash
   pnpm dlx shadcn-ui@latest add card button
   ```

## 4. Connecting Frontend and Backend

1. **Configure Next.js API Proxy (`next.config.js` or `.ts`):**
   Modify the Next config in the `frontend/` directory to proxy requests starting with `/api` to the backend running on port 8000.
   ```javascript
   /** @type {import('next').NextConfig} */
   const nextConfig = {
     async rewrites() {
       return [
         {
           // Proxy all requests starting with /api to the FastAPI backend
           source: '/api/:path*',
           destination: 'http://localhost:8000/:path*',
         },
       ]
     },
   }
   export default nextConfig;
   ```

2. **Fetch Data inside Next.js (`src/app/page.tsx`):**
   Test the connection by making a fetch request to the proxied backend `health` endpoint.
   ```tsx
   "use client";

   import { useEffect, useState } from "react";
   import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

   export default function Home() {
     const [status, setStatus] = useState<string>("Loading...");

     useEffect(() => {
       fetch("/api/health")
         .then((res) => res.json())
         .then((data) => setStatus(data.message))
         .catch((err) => setStatus("Error connecting to backend"));
     }, []);

     return (
       <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-slate-50">
         <Card className="w-96 shadow-lg">
           <CardHeader>
             <CardTitle className="text-xl">System Status</CardTitle>
           </CardHeader>
           <CardContent>
             <div className="flex items-center space-x-2">
               <div className={`h-3 w-3 rounded-full ${status === 'Backend is running!' ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'}`}></div>
               <p className="font-medium text-slate-700">{status}</p>
             </div>
           </CardContent>
         </Card>
       </main>
     );
   }
   ```

## 5. Execution and Verification Plan
1. **Start Backend:**
   ```bash
   cd backend
   uv run uvicorn app.main:app --reload --port 8000
   ```
2. **Start Frontend:**
   ```bash
   cd frontend
   pnpm dev --port 3000
   ```
3. **Verify:** Open `http://localhost:3000` in the browser. You should see a stylized Card component that initially says "Loading..." and then changes to "Backend is running!" with a green indicator, confirming the Next.js frontend has successfully communicated with the FastAPI backend through the development proxy.
