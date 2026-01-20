import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: '신준희 - 편의점같은 개발자',
  description: '빠르게 변화하는 세상에 적응하는 개발자',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}
