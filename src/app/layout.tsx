import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI 골프 부킹 어시스턴트",
  description: "수도권 골프장 예약 성공 확률을 극적으로 올려주는 AI 기반 서비스",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko">
      <body className="font-sans">{children}</body>
    </html>
  );
}
