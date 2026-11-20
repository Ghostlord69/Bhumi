package com.landregistry.store;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.context.annotation.Profile;
import org.springframework.jdbc.core.JdbcTemplate;

@Configuration
@Profile("sqlite")
public class SqliteStoreConfig {
    @Bean
    @Primary
    AppStore jdbcAppStore(JdbcTemplate jdbcTemplate) {
        return new JdbcAppStore(jdbcTemplate);
    }
}
