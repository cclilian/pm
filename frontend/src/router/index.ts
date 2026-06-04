import { createRouter, createWebHistory } from 'vue-router'

import AdminLayout from '@/layouts/AdminLayout.vue'
import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import ProjectListView from '@/views/ProjectListView.vue'
import ProjectDetailView from '@/views/ProjectDetailView.vue'
import RequirementListView from '@/views/RequirementListView.vue'
import UserListView from '@/views/UserListView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: HomeView,
          meta: { title: '工作台', requiresAuth: true },
        },
        {
          path: 'projects',
          name: 'projects',
          component: ProjectListView,
          meta: { title: '项目列表', requiresAuth: true },
        },
        {
          path: 'projects/:id',
          name: 'project-detail',
          component: ProjectDetailView,
          meta: { title: '项目详情', requiresAuth: true },
        },
        {
          path: 'projects/:id/requirements',
          name: 'project-requirements',
          component: RequirementListView,
          meta: { title: '需求管理', requiresAuth: true },
        },
        {
          path: 'settings/users',
          name: 'settings-users',
          component: UserListView,
          meta: { title: '用户管理', requiresAuth: true },
        },
        {
          path: ':pathMatch(.*)*',
          name: 'not-found',
          component: () => import('@/views/NotFoundView.vue'),
          meta: { title: '页面不存在', requiresAuth: true },
        },
      ],
    },
  ],
})

export default router
