import { auth } from "@clerk/nextjs";

export function requireUser() {
  return auth();
}
