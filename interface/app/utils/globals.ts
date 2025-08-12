export function useNotifications() {
  const toast = useToast();
  const  showToast = (title : string, desc: string, icon: string, colorV: any)  => {
    toast.add({
      title: title,
      description: desc,
      icon: icon,
      color : colorV,
      closeIcon : 'i-heroicons-x-mark',
      close: {
        color: colorV,
        variant: 'outline',
        class: 'rounded-full'
      }
    })
  }
  return {
    showToast
  };
}

export const iconAndColorFromStatus: any = {
  running: { icon: 'i-heroicons-arrow-path', bgColor: 'bg-amber-200' },
  success: { icon: 'i-heroicons-check', bgColor: 'bg-green-200' },
  error: { icon: 'i-heroicons-x-mark', bgColor: 'bg-red-200' },
}