"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, ApiError, type Session, setCsrfToken, unwrap } from "@/lib/api/client";

export const sessionKey = ["session"] as const;
export const systemInfoKey = ["system-info"] as const;

/** Current session, or null when logged out. Never throws for a 401. */
export function useSession() {
  return useQuery({
    queryKey: sessionKey,
    queryFn: async (): Promise<Session | null> => {
      const result = await api.GET("/auth/me");
      if (result.response.status === 401) {
        setCsrfToken(null);
        return null;
      }
      const session = unwrap(result);
      setCsrfToken(session.csrf_token);
      return session;
    },
    staleTime: 60_000,
    retry: false,
  });
}

export function useSystemInfo() {
  return useQuery({
    queryKey: systemInfoKey,
    queryFn: async () => unwrap(await api.GET("/system/info")),
    staleTime: 5 * 60_000,
  });
}

type LoginInput = { email: string; password: string };
type RegisterInput = LoginInput & { org_name: string; full_name: string };

function useSessionMutation<TInput>(call: (input: TInput) => Promise<Session>) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: call,
    onSuccess: (session) => {
      setCsrfToken(session.csrf_token);
      queryClient.setQueryData(sessionKey, session);
    },
  });
}

export function useLogin() {
  return useSessionMutation(async (body: LoginInput) =>
    unwrap(await api.POST("/auth/login", { body }), "Login failed"),
  );
}

export function useRegister() {
  return useSessionMutation(async (body: RegisterInput) =>
    unwrap(await api.POST("/auth/register", { body }), "Registration failed"),
  );
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { response } = await api.POST("/auth/logout");
      // 401 means the session had already expired: that's still "logged out".
      if (!response.ok && response.status !== 401) {
        throw new ApiError(response.status, "Logout failed");
      }
    },
    onSuccess: () => {
      setCsrfToken(null);
      queryClient.setQueryData(sessionKey, null);
      queryClient.removeQueries({ predicate: (query) => query.queryKey[0] !== sessionKey[0] });
    },
  });
}
