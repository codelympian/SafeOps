import {
  BarChart3,
  ClipboardCheck,
  FileText,
  LayoutDashboard,
  type LucideIcon,
  MessageSquareText,
  Settings,
  ShieldAlert,
  TriangleAlert,
} from "lucide-react";

export type NavItem = {
  href: string;
  label: string;
  icon: LucideIcon;
};

/** The eight sections from the spec, in order. */
export const NAV_ITEMS: readonly NavItem[] = [
  { href: "/overview", label: "Overview", icon: LayoutDashboard },
  { href: "/assistant", label: "HSE Assistant", icon: MessageSquareText },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/incidents", label: "Incident Library", icon: TriangleAlert },
  { href: "/jobs", label: "Job Risk Analysis", icon: ClipboardCheck },
  { href: "/risk-rules", label: "Risk Rules", icon: ShieldAlert },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function isActive(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}
