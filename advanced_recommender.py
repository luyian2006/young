"""
OpenDigger高级推荐系统 - 支持GitHub仓库分析和动态项目发现
最终优化版：用户输入 + 高匹配度
"""
import requests
import json
import os
import time
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import hashlib

class AdvancedOpenDiggerRecommender:
    def __init__(self, github_token=None):
        self.opendigger_url = "https://oss.x-lab.info/open_digger/github"
        self.github_api = "https://api.github.com"
        self.github_token = github_token
        self.headers = {"User-Agent": "OpenDigger-Recommender"}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
        
        # 初始化项目数据库（增强版）
        self.project_db = self._initialize_enhanced_project_database()
        
        # 增强技能图谱（高权重）
        self.skill_graph = self._build_enhanced_skill_graph()
        
        # 缓存
        os.makedirs("cache", exist_ok=True)
        os.makedirs("user_data", exist_ok=True)
    
    def _initialize_enhanced_project_database(self):
        """初始化增强版项目数据库"""
        return {
            # ========== 大赛工具项目 ==========
            "apache/iotdb": {
                "tags": ["Java", "时序数据库", "物联网", "大赛工具", "Apache", "大数据", 
                        "time-series", "database", "IoT", "时序数据", "工业互联网"],
                "category": "database",
                "difficulty": "intermediate",
                "description": "Apache IoTDB: 高性能时序数据库"
            },
            "X-lab2017/open-digger": {
                "tags": ["JavaScript", "开源分析", "数据可视化", "大赛工具", "metrics", 
                        "analytics", "开源生态", "数据挖掘", "GitHub分析", "数据分析"],
                "category": "analytics",
                "difficulty": "intermediate",
                "description": "OpenDigger: 开源生态数据分析平台"
            },
            "dataease/dataease": {
                "tags": ["Java", "数据可视化", "BI工具", "大赛工具", "low-code", "报表", 
                        "dashboard", "business intelligence", "数据大屏", "可视化平台"],
                "category": "visualization",
                "difficulty": "beginner",
                "description": "DataEase: 开源数据可视化分析工具"
            },
            
            # ========== AI/机器学习项目 ==========
            "pytorch/pytorch": {
                "tags": ["Python", "深度学习", "AI", "机器学习", "framework", "神经网络", 
                        "GPU计算", "research", "人工智能", "热门"],
                "category": "ai-ml",
                "difficulty": "advanced",
                "description": "PyTorch: 开源机器学习框架"
            },
            "tensorflow/tensorflow": {
                "tags": ["Python", "机器学习", "深度学习", "AI", "Google", "production", 
                        "部署", "Keras", "人工智能", "热门"],
                "category": "ai-ml",
                "difficulty": "advanced",
                "description": "TensorFlow: 开源机器学习平台"
            },
            "huggingface/transformers": {
                "tags": ["Python", "NLP", "transformer", "预训练模型", "自然语言处理", 
                        "BERT", "GPT", "大语言模型", "AI", "热门"],
                "category": "ai-ml",
                "difficulty": "intermediate",
                "description": "Transformers: 预训练自然语言处理模型"
            },
            "langchain-ai/langchain": {
                "tags": ["Python", "AI", "大语言模型", "LLM", "应用开发", "框架", 
                        "机器学习", "热门"],
                "category": "ai-ml",
                "difficulty": "intermediate",
                "description": "LangChain: 大语言模型应用开发框架"
            },
            
            # ========== 前端开发项目 ==========
            "vuejs/vue": {
                "tags": ["JavaScript", "前端框架", "响应式", "progressive", "组件化", 
                        "SPA", "MVVM", "易上手", "前端", "热门"],
                "category": "frontend",
                "difficulty": "intermediate",
                "description": "Vue.js: 渐进式JavaScript框架"
            },
            "facebook/react": {
                "tags": ["JavaScript", "前端", "UI", "component-based", "虚拟DOM", 
                        "生态丰富", "Hook", "流行", "前端", "热门"],
                "category": "frontend",
                "difficulty": "intermediate",
                "description": "React: 用于构建用户界面的JavaScript库"
            },
            "vercel/next.js": {
                "tags": ["JavaScript", "React", "SSR", "全栈", "服务端渲染", 
                        "框架", "静态生成", "现代化", "前端"],
                "category": "frontend",
                "difficulty": "intermediate",
                "description": "Next.js: React全栈框架"
            },
            
            # ========== 后端/数据库项目 ==========
            "spring-projects/spring-boot": {
                "tags": ["Java", "后端框架", "微服务", "企业级", "REST API", "Web", 
                        "依赖注入", "企业开发", "后端"],
                "category": "backend",
                "difficulty": "intermediate",
                "description": "Spring Boot: Java企业级开发框架"
            },
            "ClickHouse/ClickHouse": {
                "tags": ["C++", "OLAP", "数据库", "列式存储", "实时分析", 
                        "高性能", "大数据", "数据库"],
                "category": "database",
                "difficulty": "advanced",
                "description": "ClickHouse: 高性能列式数据库"
            },
            
            # ========== 开发工具项目 ==========
            "microsoft/vscode": {
                "tags": ["TypeScript", "编辑器", "IDE", "开发工具", "extensible", 
                        "轻量级", "插件丰富", "跨平台", "工具"],
                "category": "dev-tools",
                "difficulty": "beginner",
                "description": "VS Code: 轻量级代码编辑器"
            },
            
            # ========== 热门趋势项目 ==========
            "kubernetes/kubernetes": {
                "tags": ["Go", "容器编排", "DevOps", "云原生", "微服务", 
                        "分布式", "自动化", "热门"],
                "category": "devops",
                "difficulty": "advanced",
                "description": "Kubernetes: 容器编排平台"
            },
            "docker/compose": {
                "tags": ["Go", "容器编排", "DevOps", "多容器", "开发环境", 
                        "部署", "微服务", "工具"],
                "category": "devops",
                "difficulty": "intermediate",
                "description": "Docker Compose: 多容器Docker应用工具"
            }
        }
    
    def _build_enhanced_skill_graph(self):
        """构建增强版技能图谱（高权重）"""
        return {
            'python': {
                'related': ['django', 'flask', 'fastapi', 'pandas', 'numpy', 
                           'tensorflow', 'pytorch', '机器学习', '数据科学', '数据分析'],
                'base_weight': 20
            },
            'javascript': {
                'related': ['react', 'vue', 'angular', 'node', 'typescript', 
                           'webpack', '前端', 'web开发', 'express'],
                'base_weight': 18
            },
            'java': {
                'related': ['spring', 'spring-boot', 'hibernate', 'android', 
                           '后端开发', '企业级', '微服务', 'iotdb', 'dataease'],
                'base_weight': 18
            },
            '机器学习': {
                'related': ['深度学习', '人工智能', 'ai', '神经网络', '数据科学',
                           'python', 'tensorflow', 'pytorch'],
                'base_weight': 25
            },
            '数据科学': {
                'related': ['数据分析', '数据挖掘', '统计', '可视化', '大数据',
                           'python', 'pandas', 'numpy', '机器学习'],
                'base_weight': 22
            },
            '前端': {
                'related': ['javascript', 'react', 'vue', 'css', 'html',
                           '响应式设计', 'ui/ux', 'web开发'],
                'base_weight': 20
            },
            '大数据': {
                'related': ['hadoop', 'spark', 'hive', '数据分析', '分布式计算',
                           '数据仓库', '数据处理', 'iot', 'iotdb'],
                'base_weight': 22
            },
            '数据可视化': {
                'related': ['bi', 'dashboard', '报表', '图表', '数据分析',
                           'javascript', 'python', '数据大屏', 'dataease'],
                'base_weight': 20
            },
            '物联网': {
                'related': ['传感器', '嵌入式', '时序数据', '大数据', '实时分析',
                           'iotdb', '工业互联网'],
                'base_weight': 20
            },
            'devops': {
                'related': ['docker', 'kubernetes', 'ci/cd', 'aws', 'azure',
                           '云原生', '基础设施', '自动化'],
                'base_weight': 18
            }
        }
    
    def analyze_github_user(self, username):
        """深度分析GitHub用户 - 增强版"""
        print(f"🔍 深度分析GitHub用户: {username}")
        print("正在获取用户数据...")
        
        user_profile = {
            'username': username,
            'skills': [],
            'detailed_skills': {},
            'interests': [],
            'experience_level': 'intermediate',
            'activity_score': 0,
            'recent_repos': [],
            'starred_repos': [],
            'following_users': [],
            'analysis_time': datetime.now().isoformat()
        }
        
        try:
            # 1. 获取用户基础信息
            user_info = self._fetch_github_data(f"/users/{username}")
            if user_info:
                user_profile['name'] = user_info.get('name', username)
                user_profile['bio'] = user_info.get('bio', '')
                user_profile['public_repos'] = user_info.get('public_repos', 0)
                user_profile['followers'] = user_info.get('followers', 0)
                print(f"  👤 {user_profile['name']} - {user_profile['bio'][:50] if user_profile['bio'] else '暂无简介'}")
            
            # 2. 获取用户仓库（分析技术栈）
            print("  分析用户仓库...")
            repos = self._fetch_github_data(f"/users/{username}/repos?per_page=100&sort=updated")
            if repos:
                # 分析技术栈
                skill_analysis = self._extract_enhanced_skills_from_repos(repos)
                user_profile['skills'] = skill_analysis['primary']
                user_profile['detailed_skills'] = skill_analysis['detailed']
                user_profile['recent_repos'] = [repo['full_name'] for repo in repos[:10]]
                
                # 分析经验等级
                user_profile['experience_level'] = self._assess_enhanced_experience_level(repos)
                user_profile['activity_score'] = self._calculate_activity_score(repos)
                
                if user_profile['skills']:
                    print(f"  发现技能: {', '.join(user_profile['skills'][:8])}")
                else:
                    print("  未发现技能，使用默认技能")
                    user_profile['skills'] = ['Python', 'JavaScript', '开源开发', 'Git', '前端开发', '后端开发']
            else:
                print("  无仓库数据，使用默认技能")
                user_profile['skills'] = ['Python', 'JavaScript', '开源开发', 'Git', '前端开发', '后端开发']
            
            # 3. 获取starred项目（分析兴趣）
            print("  分析starred项目...")
            starred = self._fetch_github_data(f"/users/{username}/starred?per_page=60")
            if starred:
                user_profile['starred_repos'] = [repo['full_name'] for repo in starred[:30]]
                user_profile['interests'] = self._extract_enhanced_interests_from_starred(starred)
                
                if user_profile['interests']:
                    print(f"  发现兴趣: {', '.join(user_profile['interests'][:6])}")
                else:
                    print("  未发现兴趣，使用默认兴趣")
                    user_profile['interests'] = ['开源工具', 'Web开发', '数据科学', 'AI/机器学习', '云计算']
            else:
                print("  无starred数据，使用默认兴趣")
                user_profile['interests'] = ['开源工具', 'Web开发', '数据科学', 'AI/机器学习', '云计算']
            
            # 4. 获取用户关注的项目（following）
            following = self._fetch_github_data(f"/users/{username}/following?per_page=30")
            if following:
                user_profile['following_users'] = [user['login'] for user in following]
            
            # 5. 技能扩展（基于兴趣）
            user_profile['skills'] = self._extend_skills_based_on_interests(
                user_profile['skills'], 
                user_profile['interests']
            )
            
            print(f"✅ 分析完成! 技能数: {len(user_profile['skills'])}")
            print(f"   经验等级: {user_profile['experience_level']}")
            print(f"   活跃度: {user_profile['activity_score']:.1f}")
            
        except Exception as e:
            print(f"⚠️ GitHub分析部分失败: {e}")
            # 提供丰富的默认值
            user_profile['skills'] = ['Python', 'JavaScript', '开源开发', 'Git', 
                                     '前端开发', '后端开发', '数据科学', '机器学习']
            user_profile['interests'] = ['开源工具', 'Web开发', '数据科学', 
                                        'AI/机器学习', '云计算', '移动开发']
            user_profile['experience_level'] = 'intermediate'
            user_profile['activity_score'] = 50
        
        return user_profile
    
    def _extract_enhanced_skills_from_repos(self, repos):
        """从仓库中提取增强版技能"""
        skills_counter = Counter()
        detailed_skills = defaultdict(list)
        
        for repo in repos:
            # 编程语言（权重最高）
            language = repo.get('language')
            if language:
                skills_counter[language] += 5
                detailed_skills[language].append(repo['full_name'])
            
            # 从描述和主题中提取技术关键词
            description = repo.get('description', '').lower() if repo.get('description') else ''
            topics = repo.get('topics', [])
            
            full_text = f"{description} {' '.join(topics)}".lower()
            
            # 技术关键词检测 - 增强版
            tech_keywords = {
                'Python': {'keywords': ['python', 'django', 'flask', 'fastapi', 'pandas', 
                                       'numpy', 'scikit-learn', 'tensorflow', 'pytorch'], 'weight': 4},
                'JavaScript': {'keywords': ['javascript', 'js', 'react', 'vue', 'angular', 
                                           'node', 'express', 'typescript'], 'weight': 4},
                'Java': {'keywords': ['java', 'spring', 'spring-boot', 'hibernate', 'android'], 'weight': 4},
                'TypeScript': {'keywords': ['typescript', 'ts'], 'weight': 3},
                'Go': {'keywords': ['go', 'golang'], 'weight': 3},
                'Rust': {'keywords': ['rust'], 'weight': 2},
                '机器学习': {'keywords': ['machine learning', 'ml', 'deep learning', 'ai', 
                                       'tensorflow', 'pytorch', '神经网络', '人工智能'], 'weight': 5},
                '数据科学': {'keywords': ['data science', 'data analysis', '数据分析', '数据挖掘', 
                                        'pandas', 'numpy'], 'weight': 4},
                '前端开发': {'keywords': ['frontend', '前端', 'web', 'css', 'html', 
                                       'react', 'vue', 'angular'], 'weight': 4},
                '后端开发': {'keywords': ['backend', '后端', 'api', 'server', 'database', 
                                        '微服务', 'rest'], 'weight': 4},
                'DevOps': {'keywords': ['devops', 'docker', 'kubernetes', 'ci/cd', 
                                       'jenkins', '云原生'], 'weight': 3},
                '大数据': {'keywords': ['big data', '大数据', 'hadoop', 'spark', 'hive'], 'weight': 4},
                '数据可视化': {'keywords': ['data visualization', '可视化', 'bi', 'dashboard', 
                                         '报表', '图表'], 'weight': 3},
                '物联网': {'keywords': ['iot', '物联网', '传感器', '嵌入式', '智能家居'], 'weight': 3},
                '开源开发': {'keywords': ['open source', '开源', 'github', 'git'], 'weight': 2},
                '移动开发': {'keywords': ['mobile', 'android', 'ios', 'flutter', 'react-native'], 'weight': 3}
            }
            
            for skill, data in tech_keywords.items():
                if any(keyword in full_text for keyword in data['keywords']):
                    skills_counter[skill] += data['weight']
                    detailed_skills[skill].append(repo['full_name'])
            
            # 仓库名称中的关键词
            repo_name = repo['name'].lower()
            repo_keywords = {
                'AI': ['ai', 'ml', 'deep', 'neural', '智能'],
                '数据': ['data', 'dataset', 'database'],
                '工具': ['tool', 'utils', 'utility', 'helper'],
                '学习': ['learn', 'tutorial', 'example']
            }
            
            for category, keywords in repo_keywords.items():
                if any(keyword in repo_name for keyword in keywords):
                    skills_counter['技术热情'] = skills_counter.get('技术热情', 0) + 1
        
        # 返回最相关的技能
        primary_skills = [skill for skill, count in skills_counter.most_common(20)]
        
        return {
            'primary': primary_skills,
            'detailed': dict(detailed_skills)
        }
    
    def _extract_enhanced_interests_from_starred(self, starred_repos):
        """从starred项目中提取增强版兴趣"""
        interests = Counter()
        
        for repo in starred_repos[:40]:
            topics = repo.get('topics', [])
            interests.update(topics)
            
            # 从描述中提取兴趣
            description = repo.get('description', '').lower() if repo.get('description') else ''
            
            interest_categories = {
                'Web开发': {'keywords': ['web', 'frontend', 'backend', 'framework', 
                                        'fullstack', 'javascript', 'react', 'vue'], 'weight': 3},
                '数据科学': {'keywords': ['data', 'analysis', 'ml', 'ai', 'visualization', 
                                        '数据科学', '数据分析', '机器学习'], 'weight': 3},
                'AI/机器学习': {'keywords': ['ai', '人工智能', 'machine learning', '深度学习', 
                                          'neural', 'llm', 'gpt'], 'weight': 4},
                '移动开发': {'keywords': ['mobile', 'android', 'ios', 'flutter', 
                                        'react-native', '移动端'], 'weight': 2},
                '云计算': {'keywords': ['cloud', 'aws', 'azure', 'serverless', 
                                      '云原生', 'kubernetes', 'docker'], 'weight': 2},
                '开源工具': {'keywords': ['tools', 'utilities', 'productivity', 
                                       '效率工具', '开发工具'], 'weight': 2},
                '游戏开发': {'keywords': ['game', 'unity', 'unreal', '游戏开发'], 'weight': 1},
                '区块链': {'keywords': ['blockchain', 'crypto', 'web3', '智能合约'], 'weight': 1},
                '大数据': {'keywords': ['big data', 'hadoop', 'spark', '数据分析'], 'weight': 2},
                '物联网': {'keywords': ['iot', '物联网', '智能家居', '传感器'], 'weight': 2}
            }
            
            for category, data in interest_categories.items():
                if any(keyword in description for keyword in data['keywords']):
                    interests[category] += data['weight']
        
        # 加强热门兴趣
        for interest in list(interests.keys()):
            if interest in ['AI/机器学习', '数据科学', 'Web开发', '开源工具']:
                interests[interest] *= 1.5
        
        return [interest for interest, count in interests.most_common(15)]
    
    def _assess_enhanced_experience_level(self, repos):
        """评估增强版经验等级"""
        if not repos:
            return 'intermediate'
        
        # 根据仓库数量、star数、fork数评估
        repo_count = len(repos)
        total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
        total_forks = sum(repo.get('forks_count', 0) for repo in repos)
        
        # 考虑贡献者数量和项目复杂度
        avg_stars = total_stars / max(repo_count, 1)
        avg_forks = total_forks / max(repo_count, 1)
        
        score = (
            min(repo_count / 15, 1.0) * 0.3 +
            min(avg_stars / 30, 1.0) * 0.25 +
            min(avg_forks / 15, 1.0) * 0.25 +
            min(total_stars / 300, 1.0) * 0.2
        )
        
        if score > 0.7:
            return 'advanced'
        elif score > 0.4:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _extend_skills_based_on_interests(self, skills, interests):
        """基于兴趣扩展技能"""
        extended_skills = list(skills)
        
        for interest in interests:
            if '数据' in interest or '分析' in interest:
                if 'Python' not in extended_skills:
                    extended_skills.append('Python')
                if '数据科学' not in extended_skills:
                    extended_skills.append('数据科学')
                if '机器学习' not in extended_skills:
                    extended_skills.append('机器学习')
                    
            elif 'web' in interest.lower() or '前端' in interest:
                if 'JavaScript' not in extended_skills:
                    extended_skills.append('JavaScript')
                if '前端开发' not in extended_skills:
                    extended_skills.append('前端开发')
                    
            elif 'ai' in interest.lower() or '机器学习' in interest or '人工智能' in interest:
                if 'Python' not in extended_skills:
                    extended_skills.append('Python')
                if '机器学习' not in extended_skills:
                    extended_skills.append('机器学习')
                    
            elif '后端' in interest:
                if 'Java' not in extended_skills and 'Python' not in extended_skills:
                    extended_skills.append('Python')
                if '后端开发' not in extended_skills:
                    extended_skills.append('后端开发')
                    
            elif '物联网' in interest.lower() or 'iot' in interest.lower():
                if '大数据' not in extended_skills:
                    extended_skills.append('大数据')
                if 'Java' not in extended_skills:
                    extended_skills.append('Java')
                    
            elif '可视化' in interest:
                if '数据可视化' not in extended_skills:
                    extended_skills.append('数据可视化')
                if 'JavaScript' not in extended_skills:
                    extended_skills.append('JavaScript')
        
        # 去重
        unique_skills = []
        seen = set()
        for skill in extended_skills:
            if skill not in seen:
                unique_skills.append(skill)
                seen.add(skill)
        
        return unique_skills[:20]
    
    def recommend_projects(self, user_profile, top_n=10):
        """推荐项目 - 简化版（不使用发现功能）"""
        print(f"🚀 开始智能推荐...")
        
        all_recommendations = []
        
        print(f"📊 分析 {len(self.project_db)} 个项目...")
        
        for repo, project_info in self.project_db.items():
            try:
                # 获取OpenDigger数据
                metrics = self._fetch_opendigger_metrics(repo)
                
                # 计算匹配度
                match_score, breakdown = self._calculate_high_match_score(
                    user_profile, project_info, metrics, repo
                )
                
                # 计算健康度
                health_score = self._calculate_health_score(metrics)
                
                # 计算综合分数
                combined_score = match_score * 0.7 + health_score * 0.3
                
                # 生成推荐理由
                reason = self._generate_detailed_recommendation_reason(
                    match_score, breakdown, project_info, user_profile
                )
                
                all_recommendations.append({
                    'repo': repo,
                    'name': repo.split('/')[-1],
                    'match_score': match_score,
                    'health_score': health_score,
                    'combined_score': combined_score,
                    'category': project_info.get('category', 'unknown'),
                    'tags': project_info.get('tags', []),
                    'description': project_info.get('description', '开源项目'),
                    'difficulty': project_info.get('difficulty', 'intermediate'),
                    'metrics': metrics,
                    'score_breakdown': breakdown,
                    'recommendation_reason': reason,
                    'is_competition_tool': '大赛工具' in project_info.get('tags', [])
                })
                
            except Exception as e:
                print(f"  跳过 {repo}: {e}")
                continue
        
        # 智能排序
        final_recommendations = self._smart_sort_with_competition(all_recommendations, top_n)
        
        return final_recommendations
    
    def _calculate_high_match_score(self, user_profile, project_info, metrics, repo_name):
        """高匹配度计算算法"""
        breakdown = {}
        
        user_skills = user_profile.get('skills', [])
        user_interests = user_profile.get('interests', [])
        project_tags = [tag.lower() for tag in project_info.get('tags', [])]
        
        total_score = 0
        
        # 1. 技能匹配（权重最高）
        skill_score = self._calculate_skill_match_high(user_skills, project_tags, project_info)
        total_score += skill_score
        breakdown['skill_match'] = skill_score
        
        # 2. 兴趣匹配
        interest_score = self._calculate_interest_match_high(user_interests, project_tags)
        total_score += interest_score
        breakdown['interest_match'] = interest_score
        
        # 3. 经验适配
        experience = user_profile.get('experience_level', 'intermediate')
        difficulty = project_info.get('difficulty', 'intermediate')
        exp_score = self._calculate_experience_match_high(experience, difficulty)
        total_score += exp_score
        breakdown['experience_match'] = exp_score
        
        # 4. 项目质量加成
        health_score = self._calculate_health_score(metrics)
        quality_bonus = health_score * 0.2
        total_score += quality_bonus
        breakdown['quality_bonus'] = quality_bonus
        
        # 5. 大赛工具专项加成（非常高）
        competition_bonus = 0
        if '大赛工具' in project_info.get('tags', []):
            competition_bonus = 40  # 非常高的基础加分
            
            # 检查用户是否有相关技能
            user_skills_lower = [s.lower() for s in user_skills]
            
            # DataEase相关技能
            if any(tag in ['dataease', '数据可视化'] for tag in project_info['tags']):
                if any(skill in user_skills_lower for skill in ['数据可视化', '数据分析', 'javascript', 'java']):
                    competition_bonus += 20
            
            # IoTDB相关技能
            if any(tag in ['iotdb', '时序数据库', '物联网'] for tag in project_info['tags']):
                if any(skill in user_skills_lower for skill in ['大数据', '物联网', 'java', '数据库']):
                    competition_bonus += 20
            
            # OpenDigger相关技能
            if any(tag in ['open-digger', '开源分析'] for tag in project_info['tags']):
                if any(skill in user_skills_lower for skill in ['数据分析', 'javascript', '开源分析']):
                    competition_bonus += 20
        
        total_score += competition_bonus
        breakdown['competition_bonus'] = competition_bonus
        
        # 6. 热门技术栈加成
        hot_tech_bonus = self._calculate_hot_tech_bonus_high(user_skills, project_tags)
        total_score += hot_tech_bonus
        breakdown['hot_tech_bonus'] = hot_tech_bonus
        
        # 最终分数（可能超过100，表示高匹配）
        final_score = min(total_score, 150)
        
        return final_score, breakdown
    
    def _calculate_skill_match_high(self, user_skills, project_tags, project_info):
        """高权重技能匹配"""
        score = 0
        
        for skill in user_skills:
            skill_lower = skill.lower()
            
            # 直接匹配（非常高权重）
            if skill_lower in project_tags:
                base_score = 25  # 非常高
                
                # 检查是否是热门技能
                if skill_lower in ['python', 'javascript', '机器学习', '数据科学', '前端开发']:
                    base_score += 10
                
                # 检查是否是大赛工具相关技能
                if '大赛工具' in project_info.get('tags', []):
                    # 大赛工具相关技能额外加成
                    if skill_lower in ['java', 'javascript', '数据可视化', '大数据', '物联网']:
                        base_score += 15
                
                score += base_score
            
            # 相关技能匹配
            elif skill_lower in self.skill_graph:
                related_skills = self.skill_graph[skill_lower].get('related', [])
                for related in related_skills:
                    if related in project_tags:
                        related_score = 15  # 较高
                        
                        # 热门技能的相关技能额外加成
                        if skill_lower in ['python', 'javascript', '机器学习']:
                            related_score += 8
                        
                        score += related_score
                        break  # 只取第一个匹配的相关技能
        
        # 技能组匹配加成
        skill_groups = [
            ['python', '机器学习', '数据科学'],
            ['javascript', '前端开发', 'react', 'vue'],
            ['java', '后端开发', 'spring'],
            ['大数据', '物联网', '数据分析']
        ]
        
        for group in skill_groups:
            user_group_skills = [s.lower() for s in user_skills if s.lower() in group]
            project_group_tags = [t for t in project_tags if t in group]
            
            if len(user_group_skills) >= 2 and len(project_group_tags) >= 2:
                group_bonus = len(set(user_group_skills) & set(project_group_tags)) * 5
                score += group_bonus
        
        return min(score, 80)  # 技能匹配最高80分
    
    def _calculate_interest_match_high(self, user_interests, project_tags):
        """高权重兴趣匹配"""
        score = 0
        
        for interest in user_interests:
            interest_lower = interest.lower()
            
            # 直接匹配
            if interest_lower in project_tags:
                score += 20  # 很高
            
            # 部分匹配
            elif any(interest_lower in tag for tag in project_tags):
                score += 12  # 较高
            
            # 兴趣类别匹配
            interest_categories = {
                'web开发': ['javascript', 'react', 'vue', '前端', 'web'],
                '数据科学': ['python', '数据分析', '机器学习', 'ai', '数据科学'],
                'ai/机器学习': ['ai', '机器学习', '深度学习', '神经网络', 'python'],
                '物联网': ['iot', '物联网', '传感器', '嵌入式']
            }
            
            if interest_lower in interest_categories:
                category_keywords = interest_categories[interest_lower]
                matching_keywords = [kw for kw in category_keywords if kw in project_tags]
                if matching_keywords:
                    score += len(matching_keywords) * 6
        
        return min(score, 50)  # 兴趣匹配最高50分
    
    def _calculate_experience_match_high(self, experience, difficulty):
        """高权重经验适配"""
        # 经验-难度匹配矩阵
        experience_matrix = {
            'beginner': {'beginner': 30, 'intermediate': 15, 'advanced': 5},
            'intermediate': {'beginner': 20, 'intermediate': 25, 'advanced': 15},
            'advanced': {'beginner': 10, 'intermediate': 20, 'advanced': 30}
        }
        
        return experience_matrix.get(experience, {}).get(difficulty, 15)
    
    def _calculate_hot_tech_bonus_high(self, user_skills, project_tags):
        """高权重热门技术栈加成"""
        bonus = 0
        
        # 热门技术栈
        hot_techs = {
            '机器学习': 15,
            'ai/人工智能': 15,
            '数据科学': 12,
            'python': 10,
            'javascript': 10,
            'react': 8,
            'vue': 8,
            '大数据': 10,
            '物联网': 8
        }
        
        user_skills_lower = [s.lower() for s in user_skills]
        
        for tech, points in hot_techs.items():
            if tech in user_skills_lower and tech in project_tags:
                bonus += points
        
        return min(bonus, 30)
    
    def _calculate_health_score(self, metrics):
        """计算项目健康度"""
        score = 0
        
        # 活跃度 (40%)
        activity = metrics.get('activity', {}).get('value', 0)
        score += min(activity, 100) * 0.4
        
        # 贡献者生态 (30%)
        contributors = metrics.get('contributors', {}).get('value', 0)
        new_contributors = metrics.get('new_contributors', {}).get('value', 0)
        
        score += min(contributors / 10, 15)
        if contributors > 0:
            new_ratio = new_contributors / contributors
            score += min(new_ratio * 100, 15)
        
        # 影响力 (30%)
        openrank = metrics.get('openrank', {}).get('value', 0)
        score += min(openrank, 30)
        
        return min(score, 100)
    
    def _generate_detailed_recommendation_reason(self, match_score, breakdown, project_info, user_profile):
        """生成详细推荐理由"""
        reasons = []
        
        # 基于匹配度
        if match_score > 100:
            reasons.append("⭐️ 超强匹配!")
        elif match_score > 80:
            reasons.append("🌟 高度匹配!")
        elif match_score > 60:
            reasons.append("✨ 良好匹配")
        
        # 基于技能匹配
        skill_score = breakdown.get('skill_match', 0)
        if skill_score > 50:
            reasons.append("多项技能高度匹配")
        elif skill_score > 30:
            reasons.append("关键技能匹配")
        
        # 基于兴趣匹配
        interest_score = breakdown.get('interest_match', 0)
        if interest_score > 25:
            reasons.append("符合您的核心兴趣")
        elif interest_score > 15:
            reasons.append("符合您的兴趣领域")
        
        # 大赛工具特别标注
        tags = project_info.get('tags', [])
        if '大赛工具' in tags:
            reasons.append("🎯 开源大赛核心项目")
            comp_bonus = breakdown.get('competition_bonus', 0)
            if comp_bonus > 50:
                reasons.append("与您的技能高度相关")
            elif comp_bonus > 30:
                reasons.append("与您的技能相关")
        
        # 项目特性
        category = project_info.get('category', '')
        if category == 'ai-ml':
            reasons.append("🤖 AI/机器学习热门领域")
        elif category == 'frontend':
            reasons.append("🎨 前端开发主流技术")
        elif category == 'visualization':
            reasons.append("📊 数据可视化实用工具")
        elif category == 'database':
            reasons.append("💾 数据库技术核心")
        
        # 经验适配
        user_exp = user_profile.get('experience_level', 'intermediate')
        project_diff = project_info.get('difficulty', 'intermediate')
        if user_exp == project_diff:
            reasons.append(f"✅ 难度适合{user_exp}开发者")
        
        if not reasons:
            reasons.append("优秀的开源项目，值得学习")
        
        return " | ".join(reasons[:4])  # 最多4个理由
    
    def _smart_sort_with_competition(self, recommendations, top_n):
        """智能排序（确保大赛工具在前）"""
        if not recommendations:
            return []
        
        # 按综合分数排序
        recommendations.sort(key=lambda x: x['combined_score'], reverse=True)
        
        # 确保大赛工具在顶部
        competition_tools = [r for r in recommendations if r['is_competition_tool']]
        other_tools = [r for r in recommendations if not r['is_competition_tool']]
        
        # 如果大赛工具匹配度较低，适当提升位置
        for tool in competition_tools:
            if tool['match_score'] < 60:
                tool['combined_score'] += 20  # 提升大赛工具排名
        
        # 重新合并排序
        final_list = competition_tools + other_tools
        final_list.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return final_list[:top_n]
    
    # ========== 原有的辅助方法 ==========
    
    def _fetch_github_data(self, endpoint):
        """获取GitHub数据"""
        cache_key = hashlib.md5(endpoint.encode()).hexdigest()
        cache_file = f"cache/github_{cache_key}.json"
        
        # 检查缓存
        if os.path.exists(cache_file):
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < 3600:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    pass
        
        try:
            url = f"{self.github_api}{endpoint}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 缓存数据
                try:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                except:
                    pass
                
                return data
            elif response.status_code == 403:
                print(f"⚠️ GitHub API限制，使用缓存数据")
            else:
                print(f"⚠️ GitHub API错误 {endpoint}: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ 请求失败 {endpoint}: {e}")
        
        return None
    
    def _fetch_opendigger_metrics(self, repo):
        """获取OpenDigger指标（带缓存）"""
        cache_file = f"cache/opendigger_{repo.replace('/', '_')}.json"
        
        # 检查缓存
        if os.path.exists(cache_file):
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < 86400:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    pass
        
        metrics = {}
        key_metrics = ['activity', 'openrank', 'contributors', 'new_contributors']
        
        for metric in key_metrics:
            try:
                url = f"{self.opendigger_url}/{repo}/{metric}.json"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, dict) and data:
                        sorted_keys = sorted(data.keys())
                        latest_key = sorted_keys[-1] if sorted_keys else None
                        
                        if latest_key:
                            latest_value = data[latest_key]
                            
                            # 计算趋势
                            trend = "stable"
                            if len(sorted_keys) >= 2:
                                prev_key = sorted_keys[-2]
                                if latest_value > data[prev_key] * 1.1:
                                    trend = "up"
                                elif latest_value < data[prev_key] * 0.9:
                                    trend = "down"
                            
                            metrics[metric] = {
                                'value': latest_value,
                                'trend': trend,
                                'latest_month': latest_key
                            }
                    else:
                        metrics[metric] = {'value': data, 'trend': 'stable'}
                else:
                    metrics[metric] = {'value': 0, 'trend': 'error'}
                    
            except Exception as e:
                metrics[metric] = {'value': 0, 'trend': 'error', 'error': str(e)}
        
        # 保存到缓存
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)
        except:
            pass
        
        return metrics
    
    def _calculate_activity_score(self, repos):
        """计算用户活跃度"""
        if not repos:
            return 0
        
        recent_repos = sorted(repos, key=lambda x: x.get('updated_at', ''), reverse=True)[:10]
        
        # 根据最近更新时间评估活跃度
        recent_count = len([r for r in recent_repos if self._is_recent(r.get('updated_at', ''))])
        
        return min(recent_count / 10 * 100, 100)
    
    def _is_recent(self, date_str, days=90):
        """判断是否在近期内"""
        if not date_str:
            return False
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            delta = datetime.now() - date_obj
            return delta.days <= days
        except:
            return False

def main():
    """主函数：用户输入GitHub账号"""
    print("="*60)
    print("🤖 OpenDigger高级推荐系统")
    print("="*60)
    
    # 询问用户GitHub Token（可选）
    token = input("请输入GitHub Token（按Enter跳过，但有token可以获得更好体验）: ").strip()
    if token:
        print("✅ 使用GitHub Token")
    else:
        print("⚠️ 无Token，使用公开API（可能有速率限制）")
    
    # 初始化推荐器
    recommender = AdvancedOpenDiggerRecommender(github_token=token if token else None)
    
    while True:
        print("\n" + "-"*60)
        username = input("请输入GitHub用户名（输入'quit'退出）: ").strip()
        
        if username.lower() == 'quit':
            print("👋 感谢使用，再见！")
            break
        
        if not username:
            print("⚠️ 用户名不能为空")
            continue
        
        try:
            # 分析用户
            user_profile = recommender.analyze_github_user(username)
            
            # 获取推荐
            recommendations = recommender.recommend_projects(user_profile, top_n=8)
            
            # 打印结果
            if recommendations:
                print(f"\n🎯 为您推荐以下 {len(recommendations)} 个项目：")
                print("-"*60)
                
                for i, rec in enumerate(recommendations, 1):
                    competition_mark = "🎯" if rec['is_competition_tool'] else "  "
                    score_bar = "★" * int(rec['match_score'] / 20)
                    
                    print(f"{i}. {competition_mark} {rec['name']}")
                    print(f"   🔗 {rec['repo']}")
                    print(f"   📊 匹配度: {rec['match_score']:.1f} {score_bar}")
                    print(f"   💪 健康度: {rec['health_score']:.1f}")
                    print(f"   🏷️  标签: {', '.join(rec['tags'][:5])}")
                    print(f"   📝 {rec['recommendation_reason']}")
                    
                    # 显示详细匹配信息
                    if rec.get('score_breakdown'):
                        breakdown = rec['score_breakdown']
                        details = []
                        if breakdown.get('skill_match', 0) > 0:
                            details.append(f"技能:{breakdown['skill_match']:.0f}")
                        if breakdown.get('interest_match', 0) > 0:
                            details.append(f"兴趣:{breakdown['interest_match']:.0f}")
                        if breakdown.get('competition_bonus', 0) > 0:
                            details.append(f"大赛加成:{breakdown['competition_bonus']:.0f}")
                        if details:
                            print(f"   📈 匹配详情: {' | '.join(details)}")
                    
                    print()
            else:
                print("\n⚠️ 未生成推荐，请检查用户名是否正确")
                
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            print("请检查网络连接或用户名是否正确")

if __name__ == "__main__":
    main()