#!/usr/bin/env python3
"""
高级演示脚本
支持GitHub用户分析和项目发现
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from advanced_recommender import AdvancedOpenDiggerRecommender

def main():
    print("🚀 OpenDigger高级推荐系统 - GitHub分析版")
    print("="*70)
    
    # 获取GitHub Token（可选）
    github_token = os.environ.get('GITHUB_TOKEN')
    if github_token:
        print("✅ 检测到GitHub Token，将获得更高API限制")
    else:
        print("⚠️ 未检测到GitHub Token，API调用可能受限")
        print("   设置方法: export GITHUB_TOKEN=your_token")
    
    # 初始化推荐器
    recommender = AdvancedOpenDiggerRecommender(github_token=github_token)
    
    print("\n📋 演示模式:")
    print("  1. 分析GitHub用户并推荐")
    print("  2. 手动输入技能推荐")
    print("  3. 批量分析项目健康度")
    
    try:
        choice = input("\n请选择模式 (1-3): ").strip() or "1"
        
        if choice == "1":
            # GitHub用户分析模式
            username = input("请输入GitHub用户名: ").strip()
            if not username:
                username = "torvalds"  # 默认使用Linus的账户演示
            
            print(f"\n🔍 正在分析GitHub用户: {username}")
            
            # 分析用户
            user_profile = recommender.analyze_github_user(username)
            
            print(f"\n📊 用户画像摘要:")
            print(f"   技能: {', '.join(user_profile['skills'][:8])}")
            print(f"   兴趣: {', '.join(user_profile['interests'][:5])}")
            print(f"   经验等级: {user_profile['experience_level']}")
            print(f"   活跃度: {user_profile['activity_score']:.1f}/100")
            
            # 获取推荐（带项目发现）
            goal = input("\n🎯 请选择目标 (learn/contribute/career, 默认为learn): ").strip() or "learn"
            
            print(f"\n🚀 正在生成个性化推荐（带项目发现）...")
            recommendations = recommender.recommend_with_discovery(
                user_profile=user_profile,
                use_github_data=True,
                top_n=8
            )
            
            # 保存用户画像
            save_user_profile(user_profile, username)
            
        elif choice == "2":
            # 手动输入模式
            print("\n💡 请输入你的技能（用逗号分隔）:")
            print("例如: python, machine learning, web development")
            skills_input = input("> ").strip()
            skills = [s.strip() for s in skills_input.split(',')] if skills_input else ['python']
            
            print("\n💡 请输入你的兴趣（用逗号分隔，可选）:")
            interests_input = input("> ").strip()
            interests = [s.strip() for s in interests_input.split(',')] if interests_input else []
            
            user_profile = {
                'skills': skills,
                'interests': interests,
                'experience_level': 'intermediate',
                'activity_score': 50
            }
            
            print(f"\n🚀 基于技能推荐...")
            recommendations = recommender.recommend_with_discovery(
                user_profile=user_profile,
                use_github_data=False,  # 不使用GitHub数据
                top_n=8
            )
            
        elif choice == "3":
            # 批量分析模式
            print("\n📊 批量分析项目健康度")
            
            health_data = []
            for repo in list(recommender.project_db.keys())[:15]:
                try:
                    metrics = recommender._fetch_opendigger_metrics(repo)
                    health_score = recommender._calculate_health_score(metrics)
                    
                    health_data.append({
                        'repo': repo,
                        'health_score': health_score,
                        'activity': metrics.get('activity', {}).get('value', 0),
                        'contributors': metrics.get('contributors', {}).get('value', 0),
                        'trend': metrics.get('activity', {}).get('trend', 'stable')
                    })
                    
                    print(f"  ✓ {repo}: 健康度 {health_score:.1f}")
                except:
                    print(f"  ✗ {repo}: 分析失败")
            
            # 显示健康度排名
            print("\n🏆 项目健康度排名:")
            health_data.sort(key=lambda x: x['health_score'], reverse=True)
            for i, item in enumerate(health_data[:10], 1):
                print(f"  {i}. {item['repo']}: {item['health_score']:.1f}分")
            
            # 保存结果
            save_health_data(health_data)
            return
        
        else:
            print("❌ 无效选择，使用默认模式")
            return
        
        # 显示推荐结果
        print(f"\n{'='*70}")
        print("🎯 个性化推荐结果")
        print("="*70)
        
        discovered_count = sum(1 for rec in recommendations if rec.get('is_discovered', False))
        print(f"📈 共分析 {len(recommendations)} 个项目（其中 {discovered_count} 个为新发现）\n")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['repo']}")
            print(f"   匹配度: {rec['match_score']:.1f}/100")
            print(f"   健康度: {rec['health_score']:.1f}/100")
            print(f"   类别: {rec['category']}")
            
            if rec.get('is_discovered'):
                print(f"   🔍 新发现项目")
            
            print(f"   推荐理由: {rec['recommendation_reason']}")
            
            # 显示关键指标
            metrics = rec['metrics']
            if 'activity' in metrics:
                trend_symbol = "📈" if metrics['activity'].get('trend') == 'up' else "📉" if metrics['activity'].get('trend') == 'down' else "➡️"
                print(f"   活跃度: {metrics['activity']['value']:.1f} {trend_symbol}")
            
            print()
        
        # 保存结果
        save_recommendations(recommendations, user_profile)
        
        print(f"\n✅ 演示完成！")
        print(f"💾 结果已保存至 output/ 目录")
        
    except KeyboardInterrupt:
        print("\n\n👋 演示已中断")
    except Exception as e:
        print(f"\n❌ 出错: {e}")
        import traceback
        traceback.print_exc()

def save_user_profile(profile, username):
    """保存用户画像"""
    os.makedirs("user_data", exist_ok=True)
    
    filename = f"user_data/profile_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)
    
    print(f"💾 用户画像已保存: {filename}")

def save_recommendations(recommendations, user_profile):
    """保存推荐结果"""
    os.makedirs("output", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存完整JSON
    json_data = {
        'user_profile': user_profile,
        'recommendations': recommendations,
        'generated_at': datetime.now().isoformat(),
        'summary': {
            'total_recommendations': len(recommendations),
            'avg_match_score': sum(r['match_score'] for r in recommendations) / len(recommendations) if recommendations else 0,
            'avg_health_score': sum(r['health_score'] for r in recommendations) / len(recommendations) if recommendations else 0,
            'discovered_count': sum(1 for r in recommendations if r.get('is_discovered', False))
        }
    }
    
    json_file = f"output/recommendations_{timestamp}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown报告
    md_file = f"output/recommendations_{timestamp}.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# 开源项目智能推荐报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if 'username' in user_profile:
            f.write(f"**GitHub用户**: {user_profile['username']}\n")
        f.write(f"**技能**: {', '.join(user_profile.get('skills', []))}\n")
        f.write(f"**经验等级**: {user_profile.get('experience_level', 'N/A')}\n\n")
        
        f.write(f"## 推荐结果\n\n")
        
        for i, rec in enumerate(recommendations, 1):
            f.write(f"### {i}. {rec['repo']}\n")
            if rec.get('is_discovered'):
                f.write(f"🔍 **新发现项目**\n\n")
            
            f.write(f"- **匹配度**: {rec['match_score']:.1f}/100\n")
            f.write(f"- **健康度**: {rec['health_score']:.1f}/100\n")
            f.write(f"- **类别**: {rec['category']}\n")
            f.write(f"- **推荐理由**: {rec['recommendation_reason']}\n")
            f.write(f"- **技术栈**: {', '.join(rec['tags'][:4])}\n")
            
            metrics = rec['metrics']
            if 'activity' in metrics:
                trend = metrics['activity'].get('trend', 'stable')
                trend_text = {'up': '📈上升', 'down': '📉下降', 'stable': '➡️稳定'}.get(trend, trend)
                f.write(f"- **活跃度**: {metrics['activity']['value']:.1f} ({trend_text})\n")
            
            f.write("\n")
    
    print(f"📁 详细结果: {json_file}")
    print(f"📄 报告文件: {md_file}")

def save_health_data(health_data):
    """保存健康度数据"""
    os.makedirs("output", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output/project_health_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(health_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 健康度数据已保存: {filename}")

if __name__ == "__main__":
    # 检查依赖
    try:
        import requests
    except ImportError:
        print("❌ 需要安装requests库: pip install requests")
        sys.exit(1)
    
    main()