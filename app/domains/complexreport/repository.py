# from sqlalchemy import select, func
# from sqlalchemy.orm import Session
#
# from app.domains.posts.models import Post
# from app.domains.users.models import User
# from app.domains.categories.models import Category
# from app.domains.media.models import Attachment
# from app.domains.comments.models import Comment
#
#
# class ComplexReportRepository:
#     @staticmethod
#     def get_dynamic_report(
#             db: Session,
#             title: str | None = None,
#             username: str | None = None,
#             has_file: bool | None = None
#     ):
#         """
#         [업계 표준] 5개 테이블 조인 + 다이나믹 쿼리 통합 구현
#         """
#         # 1. SELECT 절 정의 (원하는 컬럼만 쏙쏙 뽑아 빌드합니다 - 자바 Projections와 동일)
#         stmt = select(
#             Post.id.label("post_id"),
#             Post.title.label("post_title"),
#             User.name.label("author_name"),
#             Category.name.label("category_name"),
#             Attachment.file_path.label("file_path"),
#             func.count(Comment.id).label("comment_count")  # 댓글 수는 서브쿼리나 그루핑으로 처리
#         )
#
#         # 2. 5개 테이블 조인 뼈대 구축 (Join 연쇄 체이닝)
#         stmt = (
#             stmt.join(User, Post.user_id == User.id)  # 1번째 조인 (작성자)
#             .join(Category, Post.category_id == Category.id)  # 2번째 조인 (카테고리)
#             .outerjoin(Attachment, Post.attachment_id == Attachment.id)  # 3번째 조인 (첨부파일은 없을 수도 있으니 LEFT JOIN)
#             .outerjoin(Comment, Comment.post_id == Post.id)  # 4번째 조인 (댓글 수 카운트용)
#         )
#
#         # 3. [MyBatis <if> 완벽 대체] 파이썬 if문으로 동적 조건 누적 적용
#         if title:
#             # 제목 검색 조건이 있을 때만 WHERE 절 추가
#             stmt = stmt.where(Post.title.contains(title))
#
#         if username:
#             # 조인된 User 테이블의 컬럼도 아무 문제 없이 바로 조건으로 사용 가능!
#             stmt = stmt.where(User.name == username)
#
#         if has_file is True:
#             # 파일이 무조건 있는 것만 조회하는 동적 조건
#             stmt = stmt.where(Attachment.id.is_not(None))
#         elif has_file is False:
#             # 파일이 없는 것만 조회하는 동적 조건
#             stmt = stmt.where(Attachment.id.is_(None))
#
#         # 4. GROUP BY 및 ORDER BY 마무리 조립
#         stmt = stmt.group_by(
#             Post.id, User.name, Category.name, Attachment.file_path
#         ).order_by(Post.id.desc())
#
#         # 5. 쿼리 실행 및 결과 가공
#         result = db.execute(stmt)
#
#         # 가공된 데이터 리스트 형태로 리턴 (자바 ResultMap 귀찮은 과정 필요 없음)
#         return [
#             {
#                 "post_id": row.post_id,
#                 "post_title": row.post_title,
#                 "author_name": row.author_name,
#                 "category_name": row.category_name,
#                 "file_path": row.file_path,
#                 "comment_count": row.comment_count
#             }
#             for row in result
#         ]