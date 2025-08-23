// To get the color and the icon matching a process status
export const iconAndColorFromStatus: any = {
  running: { icon: "i-heroicons-arrow-path", bgColor: "bg-amber-200" },
  success: { icon: "i-heroicons-check", bgColor: "bg-green-200" },
  failled: { icon: "i-heroicons-x-mark", bgColor: "bg-red-200" },
};

export const bgColors = [
  "bg-amber-200",
  "bg-green-200",
  "bg-red-200",
  "bg-blue-200",
  "bg-purple-200",
  "bg-pink-200",
  "bg-yellow-200",
  "bg-indigo-200",
  "bg-teal-200",
  "bg-cyan-200",
];

export function randomColor(): string {
  const index = Math.floor(Math.random() * bgColors.length);
  return bgColors[index] ?? "bg-gray-200";
}

export function formatValue(value: string | number): any {
  if (typeof value === "number" && !Number.isInteger(value)) {
    return value.toFixed(2);
  }
  return value;
}
