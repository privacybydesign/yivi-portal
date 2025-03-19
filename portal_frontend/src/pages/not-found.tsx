"use client";

import Image from "next/image";

export default function NotFound() {
  return (
    <div className="flex justify-center items-center">
      <div className="flex grow p-6 justify-center items-center">
          <Image src="/404.svg" alt="Yivi Logo" height={400} width={400} />
          <h1>Sorry this page could not be found.</h1>
      </div>
    </div>
  )
}