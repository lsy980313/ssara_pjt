package com.gae.server.domain.member;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface MemberRepository extends JpaRepository<Member, Long> {
    Optional<Member> findByEmail(String email);

    // 전화번호 형식 무관하게 비교 (하이픈 제거 후 비교)
    @Query("SELECT m FROM Member m WHERE m.name = :name AND REPLACE(m.phoneNumber, '-', '') = REPLACE(:phoneNumber, '-', '')")
    Optional<Member> findByNameAndPhoneNumber(@Param("name") String name, @Param("phoneNumber") String phoneNumber);

    // 비밀번호 재설정용: 이메일 + 이름 + 전화번호로 조회
    @Query("SELECT m FROM Member m WHERE m.email = :email AND m.name = :name AND REPLACE(m.phoneNumber, '-', '') = REPLACE(:phoneNumber, '-', '')")
    Optional<Member> findByEmailAndNameAndPhoneNumber(@Param("email") String email, @Param("name") String name, @Param("phoneNumber") String phoneNumber);
}