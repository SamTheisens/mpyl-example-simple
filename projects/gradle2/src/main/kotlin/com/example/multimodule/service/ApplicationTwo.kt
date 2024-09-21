package com.example.multimodule.service

import org.springframework.boot.CommandLineRunner
import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean


@SpringBootApplication
class ApplicationTwo {
    @Bean
    fun run(): CommandLineRunner =
        CommandLineRunner {
            println("HELLO WORLD 2 / change")
        }

}


fun main(args: Array<String>) {
    runApplication<ApplicationOne>(*args)
}
