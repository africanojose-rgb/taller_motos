import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      component: () => import('@/layouts/DashboardLayout.vue'),
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
        { path: 'configuraciones', name: 'configuraciones', component: () => import('@/views/ConfiguracionesView.vue'), meta: { requireAdmin: true } },
        { path: 'marcas', name: 'marcas', component: () => import('@/views/MarcasView.vue') },
        { path: 'clientes', name: 'clientes', component: () => import('@/views/ClientesView.vue') },
        { path: 'motocicletas', name: 'motocicletas', component: () => import('@/views/MotocicletasView.vue') },,
        { path: 'ordenes', name: 'ordenes', component: () => import('@/views/OrdenesView.vue') },
        { path: 'servicios', name: 'servicios', component: () => import('@/views/ServiciosView.vue') },
        { path: 'inventario', name: 'inventario', component: () => import('@/views/InventarioView.vue') },
        { path: 'facturas', name: 'facturas', component: () => import('@/views/FacturasView.vue') },
        { path: 'citas', name: 'citas', component: () => import('@/views/CitasView.vue') },
        { path: 'empleados', name: 'empleados', component: () => import('@/views/EmpleadosView.vue'), meta: { requireAdmin: true } },
        { path: 'comisiones', name: 'comisiones', component: () => import('@/views/ComisionesView.vue'), meta: { requireAdmin: true } },
        { path: 'reportes', name: 'reportes', component: () => import('@/views/ReportesView.vue') }
      ]
    },
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' }
  ]
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  const userRol = auth.user?.rol?.toLowerCase() || ''
  const isAdmin = userRol === 'admin' || userRol === 'administrador'
  
  if (!to.meta?.public && !auth.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && auth.isAuthenticated) {
    next('/dashboard')
  } else if (to.meta?.requireAdmin && !isAdmin) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router