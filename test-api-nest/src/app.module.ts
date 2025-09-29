import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { MongooseModule } from '@nestjs/mongoose';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { DealsModule } from './deals/deals.module';
import { LeadsModule } from './leads/leads.module';
import { ResumeLeadModule } from './resume-lead/resume-lead.module';
import { ResumeDealsModule } from './resume-deals/resume-deals.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      envFilePath: '.env.development',
      isGlobal: true,
    }),
    MongooseModule.forRoot(
      process.env.MONGO_URI || 'mongodb://localhost:27017/hubspot_data',
    ),
    DealsModule,
    LeadsModule,
    ResumeLeadModule,
    ResumeDealsModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
